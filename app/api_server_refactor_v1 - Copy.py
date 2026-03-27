from __future__ import annotations

import math
import re
import numpy as np
import pandas as pd
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.service import CopilotRequest, CopilotService
from app.tools.ads import get_campaign_performance, get_product_performance, get_previous_ads_query_filter
from app.tools.analysis import (
    add_product_status,
    add_totals_row,
    build_main_product_report,
    build_pmax_feed_vs_other_report,
    generate_google_ads_product_insights,
    generate_main_product_report_insights,
)
from app.tools.ga4 import (
    FAVI_SOURCE_MEDIUM,
    get_device_report,
    get_favi_device_report,
    get_favi_landing_pages_report,
    get_favi_overview_report,
    get_favi_product_report,
    get_landing_page_conversion_report,
    get_product_funnel_report_with_id,
    get_product_source_medium_performance_report,
    get_product_source_report_with_id,
    get_traffic_campaign_report,
)
from app.tools.meta_ads import (
    get_meta_adset_performance,
    get_meta_campaign_performance,
    get_meta_product_performance,
)

app = FastAPI(title='AI Ads Analyst API', version='refactor-v1')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


STAGE_ORDER = ["TOF", "MOF", "BOF"]
PLATFORMS = ["Google Ads", "Meta Ads"]

GOOGLE_CHANNEL_STAGE_MAP = {
    "SEARCH": ("BOF", "channel_type"),
    "SHOPPING": ("BOF", "channel_type"),
    "PERFORMANCE_MAX": ("BOF", "channel_type"),
    "HOTEL": ("BOF", "channel_type"),
    "LOCAL": ("BOF", "channel_type"),
    "SMART": ("BOF", "channel_type"),
    "MULTI_CHANNEL": ("MOF", "channel_type"),
    "DEMAND_GEN": ("TOF", "channel_type"),
    "DISCOVERY": ("TOF", "channel_type"),
    "DISPLAY": ("TOF", "channel_type"),
    "VIDEO": ("TOF", "channel_type"),
    "APP": ("MOF", "channel_type"),
    "LOCAL_SERVICES": ("BOF", "channel_type"),
}

META_OBJECTIVE_STAGE_MAP = {
    "OUTCOME_AWARENESS": ("TOF", "objective"),
    "BRAND_AWARENESS": ("TOF", "objective"),
    "REACH": ("TOF", "objective"),
    "VIDEO_VIEWS": ("TOF", "objective"),
    "AWARENESS": ("TOF", "objective"),
    "OUTCOME_TRAFFIC": ("MOF", "objective"),
    "TRAFFIC": ("MOF", "objective"),
    "ENGAGEMENT": ("MOF", "objective"),
    "OUTCOME_ENGAGEMENT": ("MOF", "objective"),
    "LEAD_GENERATION": ("MOF", "objective"),
    "LEADS": ("MOF", "objective"),
    "MESSAGES": ("MOF", "objective"),
    "LINK_CLICKS": ("MOF", "objective"),
    "OUTCOME_LEADS": ("MOF", "objective"),
    "SALES": ("BOF", "objective"),
    "OUTCOME_SALES": ("BOF", "objective"),
    "CONVERSIONS": ("BOF", "objective"),
    "PRODUCT_CATALOG_SALES": ("BOF", "objective"),
    "CATALOG_SALES": ("BOF", "objective"),
    "APP_PROMOTION": ("MOF", "objective"),
}

TOF_TERMS = ["awareness", "reach", "prospecting", "prospectare", "cold", "new customer", "lookalike", "video"]
MOF_TERMS = ["consideration", "engagement", "traffic", "warm", "education", "view content", "landing", "lp"]
BOF_TERMS = ["retarget", "remarketing", "cart", "checkout", "purchase", "sales", "conversion", "shopping", "search", "brand", "pmax", "performance max"]


def _safe_contains(value, terms):
    text = str(value or '').lower()
    return any(term in text for term in terms)


def _normalize_enum_value(value):
    text = str(value or '').strip()
    if not text:
        return ''
    text = text.replace(' ', '_').replace('-', '_')
    return text.upper()


def _normalize_google_channel_type(value):
    key = _normalize_enum_value(value)
    if not key:
        return ''
    google_channel_type_id_map = {
        '0': 'UNSPECIFIED',
        '1': 'UNKNOWN',
        '2': 'SEARCH',
        '3': 'DISPLAY',
        '4': 'SHOPPING',
        '5': 'HOTEL',
        '6': 'LOCAL',
        '7': 'SMART',
        '8': 'VIDEO',
        '9': 'MULTI_CHANNEL',
        '10': 'PERFORMANCE_MAX',
        '11': 'LOCAL_SERVICES',
        '12': 'TRAVEL',
        '13': 'DEMAND_GEN',
    }
    return google_channel_type_id_map.get(key, key)




def to_python_scalar(value):
    try:
        import numpy as np
        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            f = float(value)
            if math.isnan(f) or math.isinf(f):
                return 0.0
            return f
        if isinstance(value, (np.bool_,)):
            return bool(value)
    except Exception:
        pass
    return value


def to_python_records(records):
    clean = []
    for row in records:
        clean_row = {}
        for key, value in row.items():
            clean_row[key] = to_python_scalar(value)
        clean.append(clean_row)
    return clean


def dataframe_to_safe_records(df: pd.DataFrame):
    if df is None or df.empty:
        return []

    safe_df = df.copy()

    for col in safe_df.columns:
        series = safe_df[col]
        dtype_str = str(series.dtype)

        if pd.api.types.is_numeric_dtype(series):
            safe_df[col] = pd.to_numeric(series, errors='coerce').fillna(0)
        elif pd.api.types.is_bool_dtype(series):
            safe_df[col] = series.fillna(False)
        elif pd.api.types.is_datetime64_any_dtype(series):
            safe_df[col] = series.astype(str).replace('NaT', '')
        elif dtype_str == 'category':
            safe_df[col] = series.astype('object').fillna('')
        else:
            safe_df[col] = series.astype('object').fillna('')

    return to_python_records(safe_df.to_dict(orient='records'))

def _classify_google_campaign(row):
    channel_raw = row.get('channel_type', '')
    channel_key = _normalize_google_channel_type(channel_raw)
    if channel_key in GOOGLE_CHANNEL_STAGE_MAP:
        stage, source = GOOGLE_CHANNEL_STAGE_MAP[channel_key]
        return stage, f'{source}: {channel_key}'
    name = str(row.get('campaign_name', ''))
    if _safe_contains(name, BOF_TERMS):
        return 'BOF', 'fallback campaign_name'
    if _safe_contains(name, MOF_TERMS):
        return 'MOF', 'fallback campaign_name'
    if _safe_contains(name, TOF_TERMS):
        return 'TOF', 'fallback campaign_name'
    return 'MOF', 'fallback default'


def _classify_meta_campaign(row):
    objective_raw = row.get('objective', '')
    objective_key = _normalize_enum_value(objective_raw)
    if objective_key in META_OBJECTIVE_STAGE_MAP:
        stage, source = META_OBJECTIVE_STAGE_MAP[objective_key]
        return stage, f'{source}: {objective_key}'
    name = str(row.get('campaign_name', ''))
    if _safe_contains(name, BOF_TERMS):
        return 'BOF', 'fallback campaign_name'
    if _safe_contains(name, MOF_TERMS):
        return 'MOF', 'fallback campaign_name'
    if _safe_contains(name, TOF_TERMS):
        return 'TOF', 'fallback campaign_name'
    return 'MOF', 'fallback default'


def _prepare_google_funnel_campaigns(ads_date_range, campaign_filter):
    rows = get_campaign_performance(date_range=ads_date_range)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if campaign_filter and campaign_filter.strip():
        df = df[df['campaign_name'].astype(str).str.contains(campaign_filter.strip(), case=False, na=False)]
    if df.empty:
        return df
    stage_data = df.apply(_classify_google_campaign, axis=1, result_type='expand')
    df[['funnel_stage', 'stage_reason']] = stage_data
    df['platform'] = 'Google Ads'
    df['spend'] = df['cost']
    df['primary_conversions'] = df['conversions']
    df['primary_value'] = df['conversion_value']
    df['active'] = (df['impressions'] > 0) | (df['clicks'] > 0) | (df['spend'] > 0)
    df['channel_type_normalized'] = df['channel_type'].apply(_normalize_google_channel_type) if 'channel_type' in df.columns else ''
    return df


def _prepare_meta_funnel_campaigns(meta_date_preset, campaign_filter):
    rows = get_meta_campaign_performance(date_preset=meta_date_preset)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if campaign_filter and campaign_filter.strip():
        df = df[df['campaign_name'].astype(str).str.contains(campaign_filter.strip(), case=False, na=False)]
    if df.empty:
        return df
    stage_data = df.apply(_classify_meta_campaign, axis=1, result_type='expand')
    df[['funnel_stage', 'stage_reason']] = stage_data
    df['platform'] = 'Meta Ads'
    df['primary_conversions'] = df['purchases']
    df['primary_value'] = df['purchase_value']
    df['active'] = (df['impressions'] > 0) | (df['clicks'] > 0) | (df['spend'] > 0)
    df['objective_normalized'] = df['objective'].apply(_normalize_enum_value) if 'objective' in df.columns else ''
    return df


def _build_stage_summary(df_all):
    if df_all.empty:
        return pd.DataFrame()
    active_df = df_all[df_all['active']].copy()
    if active_df.empty:
        return pd.DataFrame()
    grouped = (
        active_df.groupby(['platform', 'funnel_stage'], as_index=False)
        .agg(
            active_campaigns=('campaign_name', 'nunique'),
            impressions=('impressions', 'sum'),
            clicks=('clicks', 'sum'),
            spend=('spend', 'sum'),
            conversions=('primary_conversions', 'sum'),
            conversion_value=('primary_value', 'sum'),
        )
    )
    grouped['ctr'] = grouped.apply(lambda x: round((x['clicks'] / x['impressions']) * 100, 2) if x['impressions'] else 0, axis=1)
    grouped['cpa'] = grouped.apply(lambda x: round(x['spend'] / x['conversions'], 2) if x['conversions'] else 0, axis=1)
    grouped['roas'] = grouped.apply(lambda x: round(x['conversion_value'] / x['spend'], 2) if x['spend'] else 0, axis=1)
    grouped['funnel_stage'] = pd.Categorical(grouped['funnel_stage'], categories=STAGE_ORDER, ordered=True)
    return grouped.sort_values(['platform', 'funnel_stage'])


def _stage_status(campaign_count):
    if campaign_count <= 0:
        return 'Missing'
    if campaign_count == 1:
        return 'Thin'
    return 'Covered'


def _build_stage_matrix(summary_df):
    rows = []
    for stage in STAGE_ORDER:
        row = {'stage': stage}
        total_count = 0
        total_spend = 0.0
        for platform in PLATFORMS:
            match = summary_df[(summary_df['platform'] == platform) & (summary_df['funnel_stage'].astype(str) == stage)]
            count = int(match['active_campaigns'].sum()) if not match.empty else 0
            spend = float(match['spend'].sum()) if not match.empty else 0.0
            total_count += count
            total_spend += spend
            key = platform.lower().replace(' ', '_')
            row[f'{key}_status'] = _stage_status(count)
            row[f'{key}_campaigns'] = count
            row[f'{key}_spend'] = round(spend, 2)
        row['overall_status'] = _stage_status(total_count)
        row['total_active_campaigns'] = total_count
        row['total_spend'] = round(total_spend, 2)
        rows.append(row)
    return pd.DataFrame(rows)


def _build_recommendations(summary_df):
    if summary_df.empty:
        return pd.DataFrame([{
            'priority': 'High',
            'gap': 'Nu există campanii active în intervalul selectat',
            'recommendation': 'Verifică filtrele și intervalele sau pornește campaniile înainte de analiza funnel.',
        }])
    recommendations = []
    stage_totals = {stage: int(summary_df[summary_df['funnel_stage'].astype(str) == stage]['active_campaigns'].sum()) for stage in STAGE_ORDER}
    stage_spend = {stage: float(summary_df[summary_df['funnel_stage'].astype(str) == stage]['spend'].sum()) for stage in STAGE_ORDER}
    total_spend = sum(stage_spend.values())
    if stage_totals['TOF'] == 0:
        recommendations.append({'priority': 'High', 'gap': 'Lipsește TOF', 'recommendation': 'Adaugă campanii de prospectare / awareness pentru a alimenta audiențele noi.'})
    if stage_totals['MOF'] == 0:
        recommendations.append({'priority': 'High', 'gap': 'Lipsește MOF', 'recommendation': 'Adaugă campanii de consideration / trafic cald pentru a lega prospectarea de conversie.'})
    if stage_totals['BOF'] == 0:
        recommendations.append({'priority': 'High', 'gap': 'Lipsește BOF', 'recommendation': 'Adaugă campanii de conversie / remarketing / shopping pentru a monetiza cererea.'})
    if stage_totals['TOF'] > 0 and stage_totals['BOF'] > 0 and stage_totals['MOF'] == 0:
        recommendations.append({'priority': 'Medium', 'gap': 'Funnel sărit din TOF în BOF', 'recommendation': 'Testează un strat MOF cu trafic cald, LP dedicate sau engaged audiences.'})
    if total_spend > 0:
        tof_share = stage_spend['TOF'] / total_spend
        bof_share = stage_spend['BOF'] / total_spend
        if bof_share > 0.65 and tof_share < 0.15:
            recommendations.append({'priority': 'Medium', 'gap': 'Buget prea concentrat în BOF', 'recommendation': 'Crește investiția în TOF pentru a genera cerere nouă, nu doar a consuma cererea existentă.'})
    for platform in PLATFORMS:
        for stage, label in [('TOF', 'prospectare'), ('MOF', 'consideration'), ('BOF', 'conversie')]:
            count = int(summary_df[(summary_df['platform'] == platform) & (summary_df['funnel_stage'].astype(str) == stage)]['active_campaigns'].sum())
            if count == 0:
                recommendations.append({'priority': 'Low', 'gap': f'{platform} nu acoperă {stage}', 'recommendation': f'Ia în calcul o campanie suplimentară de {label} pe {platform} pentru acoperire mai echilibrată.'})
    if not recommendations:
        recommendations.append({'priority': 'OK', 'gap': 'Funnel acoperit rezonabil', 'recommendation': 'Ai acoperire pe TOF / MOF / BOF. Următorul pas este optimizarea eficienței.'})
    return pd.DataFrame(recommendations)


def _build_campaign_table(df_all):
    if df_all.empty:
        return pd.DataFrame()
    active_df = df_all[df_all['active']].copy()
    if active_df.empty:
        return pd.DataFrame()
    active_df['ctr'] = active_df.apply(lambda x: round((x['clicks'] / x['impressions']) * 100, 2) if x['impressions'] else 0, axis=1)
    active_df['cpa'] = active_df.apply(lambda x: round(x['spend'] / x['primary_conversions'], 2) if x['primary_conversions'] else 0, axis=1)
    active_df['roas'] = active_df.apply(lambda x: round(x['primary_value'] / x['spend'], 2) if x['spend'] else 0, axis=1)
    active_df['funnel_stage'] = pd.Categorical(active_df['funnel_stage'], categories=STAGE_ORDER, ordered=True)
    active_df['signal'] = active_df.apply(lambda row: row.get('channel_type_normalized') if row.get('platform') == 'Google Ads' else row.get('objective_normalized'), axis=1)
    return active_df[[
        'platform', 'funnel_stage', 'campaign_name', 'signal', 'stage_reason',
        'impressions', 'clicks', 'spend', 'primary_conversions', 'primary_value', 'ctr', 'cpa', 'roas'
    ]].sort_values(['funnel_stage', 'platform', 'spend'], ascending=[True, True, False])



def _get_previous_meta_date_preset(current_preset: str) -> str:
    preset = str(current_preset or '').strip().lower()
    mapping = {
        'today': 'yesterday',
        'last_7d': 'last_14d',
        'last_14d': 'last_30d',
        'last_30d': 'last_month',
        'this_month': 'last_month',
    }
    return mapping.get(preset, '')


def _safe_ratio_delta(current: float, previous: float) -> float:
    if previous in (0, None):
        return 0.0
    return round(((current - previous) / previous) * 100, 2)


def _build_comparison_payload(current_summary_df, previous_summary_df, ads_date_range: str, meta_date_range: str):
    if current_summary_df is None or current_summary_df.empty:
        return {
            'available': False,
            'reason': 'Nu există suficiente date curente pentru comparație.',
            'current_ads_range': ads_date_range,
            'previous_ads_range': '',
            'current_meta_range': meta_date_range,
            'previous_meta_range': '',
            'metrics': [],
            'stage_spend': [],
            'platform_spend': [],
        }

    if previous_summary_df is None or previous_summary_df.empty:
        return {
            'available': False,
            'reason': 'Nu există suficiente date pentru perioada anterioară.',
            'current_ads_range': ads_date_range,
            'previous_ads_range': '',
            'current_meta_range': meta_date_range,
            'previous_meta_range': '',
            'metrics': [],
            'stage_spend': [],
            'platform_spend': [],
        }

    def metric_row(label, current, previous):
        current = round(float(current or 0), 2)
        previous = round(float(previous or 0), 2)
        delta = round(current - previous, 2)
        return {
            'label': label,
            'current': current,
            'previous': previous,
            'delta': delta,
            'delta_pct': _safe_ratio_delta(current, previous),
        }

    current_active = float(current_summary_df['active_campaigns'].sum()) if 'active_campaigns' in current_summary_df.columns else 0.0
    prev_active = float(previous_summary_df['active_campaigns'].sum()) if 'active_campaigns' in previous_summary_df.columns else 0.0
    current_spend = float(current_summary_df['spend'].sum()) if 'spend' in current_summary_df.columns else 0.0
    prev_spend = float(previous_summary_df['spend'].sum()) if 'spend' in previous_summary_df.columns else 0.0
    current_clicks = float(current_summary_df['clicks'].sum()) if 'clicks' in current_summary_df.columns else 0.0
    prev_clicks = float(previous_summary_df['clicks'].sum()) if 'clicks' in previous_summary_df.columns else 0.0
    current_conv = float(current_summary_df['conversions'].sum()) if 'conversions' in current_summary_df.columns else 0.0
    prev_conv = float(previous_summary_df['conversions'].sum()) if 'conversions' in previous_summary_df.columns else 0.0
    current_value = float(current_summary_df['conversion_value'].sum()) if 'conversion_value' in current_summary_df.columns else 0.0
    prev_value = float(previous_summary_df['conversion_value'].sum()) if 'conversion_value' in previous_summary_df.columns else 0.0
    current_roas = (current_value / current_spend) if current_spend else 0.0
    prev_roas = (prev_value / prev_spend) if prev_spend else 0.0

    metric_rows = [
        metric_row('Active campaigns', current_active, prev_active),
        metric_row('Spend', current_spend, prev_spend),
        metric_row('Clicks', current_clicks, prev_clicks),
        metric_row('Conversions', current_conv, prev_conv),
        metric_row('Conversion value', current_value, prev_value),
        metric_row('ROAS', current_roas, prev_roas),
    ]

    stage_rows = []
    for stage in STAGE_ORDER:
        current_stage = current_summary_df[current_summary_df['funnel_stage'].astype(str) == stage]
        prev_stage = previous_summary_df[previous_summary_df['funnel_stage'].astype(str) == stage]
        current_stage_spend = float(current_stage['spend'].sum()) if not current_stage.empty else 0.0
        prev_stage_spend = float(prev_stage['spend'].sum()) if not prev_stage.empty else 0.0
        stage_rows.append({
            'label': stage,
            'current': round(current_stage_spend, 2),
            'previous': round(prev_stage_spend, 2),
            'delta': round(current_stage_spend - prev_stage_spend, 2),
            'delta_pct': _safe_ratio_delta(current_stage_spend, prev_stage_spend),
        })

    platform_rows = []
    for platform in PLATFORMS:
        current_platform = current_summary_df[current_summary_df['platform'] == platform]
        prev_platform = previous_summary_df[previous_summary_df['platform'] == platform]
        current_platform_spend = float(current_platform['spend'].sum()) if not current_platform.empty else 0.0
        prev_platform_spend = float(prev_platform['spend'].sum()) if not prev_platform.empty else 0.0
        platform_rows.append({
            'label': platform,
            'current': round(current_platform_spend, 2),
            'previous': round(prev_platform_spend, 2),
            'delta': round(current_platform_spend - prev_platform_spend, 2),
            'delta_pct': _safe_ratio_delta(current_platform_spend, prev_platform_spend),
        })

    return {
        'available': True,
        'reason': '',
        'current_ads_range': ads_date_range,
        'previous_ads_range': get_previous_ads_query_filter(ads_date_range),
        'current_meta_range': meta_date_range,
        'previous_meta_range': _get_previous_meta_date_preset(meta_date_range),
        'metrics': metric_rows,
        'stage_spend': stage_rows,
        'platform_spend': platform_rows,
    }




def get_previous_ads_preset_for_funnel(current_filter: str) -> str:
    value = str(current_filter or '').upper().strip()

    mapping = {
        'LAST_7_DAYS': 'LAST_14_DAYS',
        'LAST_30_DAYS': 'LAST_MONTH',
        'THIS_MONTH': 'LAST_MONTH',
    }

    return mapping.get(value, '')


def _funnel_coverage_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    try:
        campaign_filter = f.get('campaignFilter', '')
        ads_date_range = f['adsDateRange']
        meta_date_range = f['metaDateRange']
        compare_previous = bool(f.get('comparePrevious', False))

        google_df = _prepare_google_funnel_campaigns(ads_date_range=ads_date_range, campaign_filter=campaign_filter)
        meta_df = _prepare_meta_funnel_campaigns(meta_date_preset=meta_date_range, campaign_filter=campaign_filter)

        if google_df.empty and meta_df.empty:
            return {
                'metrics': {'active_campaigns': 0, 'covered_stages': 0, 'total_spend': 0.0, 'total_conversions': 0.0},
                'matrix': [],
                'recommendations': [],
                'summary': [],
                'campaigns': [],
                'comparison': {
                    'available': False,
                    'reason': 'Nu există campanii active în intervalul selectat.',
                    'current_ads_range': ads_date_range,
                    'previous_ads_range': '',
                    'current_meta_range': meta_date_range,
                    'previous_meta_range': '',
                    'metrics': [],
                    'stage_spend': [],
                    'platform_spend': [],
                },
                'methodology': {
                    'google_ads': 'Clasificare după advertising_channel_type (inclusiv raw enum ID mapat). campaign_name este fallback.',
                    'meta_ads': 'Clasificare după objective. campaign_name este fallback.',
                },
            }

        df_all = pd.concat([google_df, meta_df], ignore_index=True)
        summary_df = _build_stage_summary(df_all)
        matrix_df = _build_stage_matrix(summary_df)
        recommendations_df = _build_recommendations(summary_df)
        campaigns_df = _build_campaign_table(df_all)

        total_active = int(campaigns_df['campaign_name'].nunique()) if not campaigns_df.empty else 0
        total_spend = float(campaigns_df['spend'].sum()) if not campaigns_df.empty else 0.0
        total_conversions = float(campaigns_df['primary_conversions'].sum()) if not campaigns_df.empty else 0.0
        covered_stages = int((matrix_df['total_active_campaigns'] > 0).sum()) if not matrix_df.empty else 0

        # Previous-period comparison
        previous_summary_df = pd.DataFrame()
        comparison_payload = {
            'available': False,
            'reason': 'Comparația cu perioada anterioară este dezactivată.',
            'current_ads_range': ads_date_range,
            'previous_ads_range': '',
            'current_meta_range': meta_date_range,
            'previous_meta_range': '',
            'metrics': [],
            'stage_spend': [],
            'platform_spend': [],
        }

        if compare_previous:
            prev_ads_filter = get_previous_ads_preset_for_funnel(ads_date_range)
            prev_meta_preset = _get_previous_meta_date_preset(meta_date_range)

            prev_google_df = _prepare_google_funnel_campaigns(ads_date_range=prev_ads_filter, campaign_filter=campaign_filter) if prev_ads_filter else pd.DataFrame()
            prev_meta_df = _prepare_meta_funnel_campaigns(meta_date_preset=prev_meta_preset or meta_date_range, campaign_filter=campaign_filter) if prev_meta_preset else pd.DataFrame()

            if not prev_google_df.empty or not prev_meta_df.empty:
                previous_all = pd.concat([x for x in [prev_google_df, prev_meta_df] if not x.empty], ignore_index=True)
                previous_summary_df = _build_stage_summary(previous_all)

            comparison_payload = _build_comparison_payload(summary_df, previous_summary_df, ads_date_range, meta_date_range)

        return {
            'metrics': {k: to_python_scalar(v) for k, v in {
                'active_campaigns': total_active,
                'covered_stages': covered_stages,
                'total_spend': round(total_spend, 2),
                'total_conversions': round(total_conversions, 2),
            }.items()},
            'matrix': dataframe_to_safe_records(matrix_df),
            'recommendations': dataframe_to_safe_records(recommendations_df),
            'summary': dataframe_to_safe_records(summary_df),
            'campaigns': dataframe_to_safe_records(campaigns_df),
            'comparison': {
                'available': comparison_payload.get('available', False),
                'reason': comparison_payload.get('reason', ''),
                'current_ads_range': comparison_payload.get('current_ads_range', ads_date_range),
                'previous_ads_range': comparison_payload.get('previous_ads_range', ''),
                'current_meta_range': comparison_payload.get('current_meta_range', meta_date_range),
                'previous_meta_range': comparison_payload.get('previous_meta_range', ''),
                'metrics': to_python_records(comparison_payload.get('metrics', [])),
                'stage_spend': to_python_records(comparison_payload.get('stage_spend', [])),
                'platform_spend': to_python_records(comparison_payload.get('platform_spend', [])),
            },
            'methodology': {
                'google_ads': 'Clasificare după advertising_channel_type (inclusiv raw enum ID mapat). campaign_name este fallback.',
                'meta_ads': 'Clasificare după objective. campaign_name este fallback.',
            },
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'metrics': {'active_campaigns': 0, 'covered_stages': 0, 'total_spend': 0.0, 'total_conversions': 0.0},
            'matrix': [],
            'recommendations': [],
            'summary': [],
            'campaigns': [],
            'comparison': {
                'available': False,
                'reason': '',
                'current_ads_range': f.get('adsDateRange', ''),
                'previous_ads_range': '',
                'current_meta_range': f.get('metaDateRange', ''),
                'previous_meta_range': '',
                'metrics': [],
                'stage_spend': [],
                'platform_spend': [],
            },
            'methodology': {
                'google_ads': 'Clasificare după advertising_channel_type (inclusiv raw enum ID mapat). campaign_name este fallback.',
                'meta_ads': 'Clasificare după objective. campaign_name este fallback.',
            },
            'error': str(e),
        }




def _add_session_rates(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    if {'engaged_sessions', 'sessions'}.issubset(df.columns):
        df['engagement_rate'] = df.apply(lambda x: round((x['engaged_sessions'] / x['sessions']) * 100, 2) if x['sessions'] else 0, axis=1)
    if {'purchase_revenue', 'sessions'}.issubset(df.columns):
        df['revenue_per_session'] = df.apply(lambda x: round(x['purchase_revenue'] / x['sessions'], 2) if x['sessions'] else 0, axis=1)
    if {'purchases', 'sessions'}.issubset(df.columns):
        df['purchase_rate'] = df.apply(lambda x: round((x['purchases'] / x['sessions']) * 100, 2) if x['sessions'] else 0, axis=1)
    return df


def _add_product_rates(df: pd.DataFrame, views_col='items_viewed', atc_col='items_added_to_cart', purchases_col='items_purchased', revenue_col='item_revenue') -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df['view_to_cart_rate'] = df.apply(lambda x: round((x[atc_col] / x[views_col]) * 100, 2) if x[views_col] else 0, axis=1)
    df['view_to_purchase_rate'] = df.apply(lambda x: round((x[purchases_col] / x[views_col]) * 100, 2) if x[views_col] else 0, axis=1)
    if revenue_col in df.columns:
        df['revenue_per_view'] = df.apply(lambda x: round(x[revenue_col] / x[views_col], 2) if x[views_col] else 0, axis=1)
    return df

def to_python_scalar(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return 0.0
        return f
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def to_python_records(records):
    clean = []
    for row in records:
        clean_row = {}
        for key, value in row.items():
            clean_row[key] = to_python_scalar(value)
        clean.append(clean_row)
    return clean


def _normalize_enum_value(value):
    text = str(value or '').strip()
    if not text:
        return ''
    text = text.replace(' ', '_').replace('-', '_')
    return text.upper()


def _normalize_google_channel_type(value):
    key = _normalize_enum_value(value)
    if not key:
        return ''

    google_channel_type_id_map = {
        '0': 'UNSPECIFIED',
        '1': 'UNKNOWN',
        '2': 'SEARCH',
        '3': 'DISPLAY',
        '4': 'SHOPPING',
        '5': 'HOTEL',
        '6': 'LOCAL',
        '7': 'SMART',
        '8': 'VIDEO',
        '9': 'MULTI_CHANNEL',
        '10': 'PERFORMANCE_MAX',
        '11': 'LOCAL_SERVICES',
        '12': 'TRAVEL',
        '13': 'DEMAND_GEN',
    }

    return google_channel_type_id_map.get(key, key)


def _get_pmax_campaign_names(date_range: str) -> list[str]:
    campaigns = get_campaign_performance(date_range=date_range)
    campaigns_df = pd.DataFrame(campaigns)

    if campaigns_df.empty or 'campaign_name' not in campaigns_df.columns or 'channel_type' not in campaigns_df.columns:
        return []

    campaigns_df['campaign_name'] = campaigns_df['campaign_name'].fillna('').astype(str)
    campaigns_df['channel_type_normalized'] = campaigns_df['channel_type'].apply(_normalize_google_channel_type)

    pmax_df = campaigns_df[campaigns_df['channel_type_normalized'] == 'PERFORMANCE_MAX'].copy()
    if pmax_df.empty:
        return []

    return sorted(
        pmax_df['campaign_name']
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )





def get_previous_ads_preset_for_overview(current_filter: str) -> str:
    value = str(current_filter or '').upper().strip()
    mapping = {
        'LAST_7_DAYS': 'LAST_14_DAYS',
        'LAST_30_DAYS': 'LAST_MONTH',
        'THIS_MONTH': 'LAST_MONTH',
    }
    return mapping.get(value, '')


def get_previous_pmax_ads_preset(current_filter: str) -> str:
    value = str(current_filter or '').upper().strip()
    mapping = {
        'LAST_7_DAYS': 'LAST_WEEK_SUN_SAT',
        'LAST_14_DAYS': 'LAST_30_DAYS',
        'LAST_30_DAYS': 'LAST_MONTH',
        'THIS_MONTH': 'LAST_MONTH',
    }
    return mapping.get(value, '')


def get_previous_meta_preset_for_overview(current_filter: str) -> str:
    value = str(current_filter or '').strip().lower()
    mapping = {
        'today': 'yesterday',
        'yesterday': '',
        'last_7d': 'last_14d',
        'last_14d': 'last_30d',
        'last_30d': 'last_month',
        'this_month': 'last_month',
        'last_month': '',
    }
    return mapping.get(value, '')


def get_previous_ga4_range_for_overview(start_date: str, end_date: str):
    start = str(start_date or '').strip().lower()
    end = str(end_date or '').strip().lower()

    m_start = re.match(r'^(\d+)daysago$', start)
    m_end = re.match(r'^(\d+)daysago$', end)

    if m_start and end == 'today':
        days = int(m_start.group(1))
        return f'{days * 2}daysAgo', f'{days + 1}daysAgo'

    if m_start and m_end:
        start_days = int(m_start.group(1))
        end_days = int(m_end.group(1))
        window = start_days - end_days
        if window > 0:
            return f'{start_days + window + 1}daysAgo', f'{end_days + window + 1}daysAgo'

    return '', ''


def _fetch_ga4_product_source_df(start_date: str, end_date: str) -> pd.DataFrame:
    ga4_response = get_product_source_report_with_id(start_date=start_date, end_date=end_date)
    ga4_rows = []
    for row in ga4_response.rows:
        ga4_rows.append({
            'item_id': row.dimension_values[0].value,
            'item_name': row.dimension_values[1].value,
            'source_medium': row.dimension_values[2].value,
            'items_viewed': int(row.metric_values[0].value),
            'items_added_to_cart': int(row.metric_values[1].value),
            'items_purchased': int(row.metric_values[2].value),
            'item_revenue': float(row.metric_values[3].value),
        })
    return pd.DataFrame(ga4_rows)


def _build_overview_payload(f: Dict[str, Any]) -> Dict[str, Any]:
    ads_df = pd.DataFrame(get_product_performance(date_range=f['adsDateRange']))
    ga4_df = _fetch_ga4_product_source_df(start_date=f['ga4Start'], end_date=f['ga4End'])

    campaign_filter = str(f.get('campaignFilter', '') or '').strip()
    product_filter = str(f.get('productFilter', '') or '').strip()
    selected_item_id = str(f.get('selectedItemId', '') or '').strip()

    if campaign_filter and not ads_df.empty:
        ads_df = ads_df[ads_df['campaign_name'].astype(str).str.contains(campaign_filter, case=False, na=False)]

    if selected_item_id:
        if not ads_df.empty and 'product_item_id' in ads_df.columns:
            ads_df = ads_df[ads_df['product_item_id'].astype(str) == selected_item_id]
        if not ga4_df.empty and 'item_id' in ga4_df.columns:
            ga4_df = ga4_df[ga4_df['item_id'].astype(str) == selected_item_id]
    elif product_filter:
        if not ads_df.empty and 'product_title' in ads_df.columns:
            ads_df = ads_df[ads_df['product_title'].astype(str).str.contains(product_filter, case=False, na=False)]
        if not ga4_df.empty and 'item_name' in ga4_df.columns:
            ga4_df = ga4_df[ga4_df['item_name'].astype(str).str.contains(product_filter, case=False, na=False)]

    report_df = add_product_status(build_main_product_report(ads_df, ga4_df))

    if report_df.empty:
        return {
            'metrics': {
                'ads_cost': 0.0,
                'ads_conversions': 0.0,
                'ads_value': 0.0,
                'ads_roas': 0.0,
                'ga4_views': 0,
                'ga4_add_to_cart': 0,
                'ga4_purchases': 0,
            },
            'funnel': [
                {'label': 'Views', 'value': 0},
                {'label': 'Add To Cart', 'value': 0},
                {'label': 'Purchases', 'value': 0},
            ],
            'top_roas': [],
            'problem_products': [],
        }

    total_ads_cost = round(float(report_df['cost'].sum()), 2)
    total_ads_conversions = round(float(report_df['conversions'].sum()), 2)
    total_ads_value = round(float(report_df['conversion_value'].sum()), 2)
    total_ads_roas = round(total_ads_value / total_ads_cost, 2) if total_ads_cost else 0.0
    total_views = int(report_df['ga4_views_total'].sum())
    total_atc = int(report_df['ga4_atc_total'].sum())
    total_purchases = int(report_df['ga4_purchases_total'].sum())

    top_roas_df = report_df.sort_values('ads_roas', ascending=False).head(10)
    problem_products_df = report_df[(report_df['cost'] > 200) & (report_df['conversions'] == 0)].sort_values('cost', ascending=False).head(10)

    return {
        'metrics': {
            'ads_cost': total_ads_cost,
            'ads_conversions': total_ads_conversions,
            'ads_value': total_ads_value,
            'ads_roas': total_ads_roas,
            'ga4_views': total_views,
            'ga4_add_to_cart': total_atc,
            'ga4_purchases': total_purchases,
        },
        'funnel': [
            {'label': 'Views', 'value': total_views},
            {'label': 'Add To Cart', 'value': total_atc},
            {'label': 'Purchases', 'value': total_purchases},
        ],
        'top_roas': dataframe_to_safe_records(top_roas_df),
        'problem_products': dataframe_to_safe_records(problem_products_df),
    }


def _build_metric_delta(current_value, previous_value):
    current_num = float(current_value or 0)
    previous_num = float(previous_value or 0)
    abs_delta = round(current_num - previous_num, 2)
    pct_delta = round((abs_delta / previous_num) * 100, 2) if previous_num else None
    return {
        'current': to_python_scalar(current_num),
        'previous': to_python_scalar(previous_num),
        'abs': to_python_scalar(abs_delta),
        'pct': to_python_scalar(pct_delta) if pct_delta is not None else None,
    }

def _overview_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    current_payload = _build_overview_payload(f)
    compare_previous = bool(f.get('comparePrevious', False))

    comparison = {
        'available': False,
        'previous_metrics': {},
        'metric_deltas': {},
        'current_ads_range': f.get('adsDateRange', ''),
        'previous_ads_range': '',
        'current_meta_range': f.get('metaDateRange', ''),
        'previous_meta_range': '',
        'current_ga4_start': f.get('ga4Start', ''),
        'current_ga4_end': f.get('ga4End', ''),
        'previous_ga4_start': '',
        'previous_ga4_end': '',
    }

    if compare_previous:
        prev_ads_range = get_previous_ads_preset_for_overview(f.get('adsDateRange', ''))
        prev_meta_range = get_previous_meta_preset_for_overview(f.get('metaDateRange', ''))
        prev_ga4_start, prev_ga4_end = get_previous_ga4_range_for_overview(f.get('ga4Start', ''), f.get('ga4End', ''))

        if prev_ads_range and prev_ga4_start and prev_ga4_end:
            previous_filters = {
                **f,
                'adsDateRange': prev_ads_range,
                'metaDateRange': prev_meta_range or f.get('metaDateRange', ''),
                'ga4Start': prev_ga4_start,
                'ga4End': prev_ga4_end,
                'comparePrevious': False,
            }
            previous_payload = _build_overview_payload(previous_filters)
            current_metrics = current_payload.get('metrics', {})
            previous_metrics = previous_payload.get('metrics', {})
            metric_keys = [
                'ads_cost',
                'ads_conversions',
                'ads_value',
                'ads_roas',
                'ga4_views',
                'ga4_add_to_cart',
                'ga4_purchases',
            ]
            comparison = {
                'available': True,
                'previous_metrics': {k: to_python_scalar(previous_metrics.get(k, 0)) for k in metric_keys},
                'metric_deltas': {k: _build_metric_delta(current_metrics.get(k, 0), previous_metrics.get(k, 0)) for k in metric_keys},
                'current_ads_range': f.get('adsDateRange', ''),
                'previous_ads_range': prev_ads_range,
                'current_meta_range': f.get('metaDateRange', ''),
                'previous_meta_range': prev_meta_range,
                'current_ga4_start': f.get('ga4Start', ''),
                'current_ga4_end': f.get('ga4End', ''),
                'previous_ga4_start': prev_ga4_start,
                'previous_ga4_end': prev_ga4_end,
            }

    return {
        **current_payload,
        'comparison': comparison,
    }

def _google_ads_campaigns_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.DataFrame(get_campaign_performance(date_range=f['adsDateRange']))
    if f['campaignFilter'].strip() and not df.empty:
        df = df[df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    if df.empty:
        return {'metrics': {'cost': 0, 'conversions': 0, 'value': 0, 'roas': 0}, 'rows': []}
    df['ctr'] = df.apply(lambda x: round((x['clicks'] / x['impressions']) * 100, 2) if x['impressions'] else 0, axis=1)
    df['cpa'] = df.apply(lambda x: round(x['cost'] / x['conversions'], 2) if x['conversions'] else 0, axis=1)
    df['roas'] = df.apply(lambda x: round(x['conversion_value'] / x['cost'], 2) if x['cost'] else 0, axis=1)
    total_cost = round(df['cost'].sum(), 2)
    total_conversions = round(df['conversions'].sum(), 2)
    total_value = round(df['conversion_value'].sum(), 2)
    total_roas = round(total_value / total_cost, 2) if total_cost else 0
    return {'metrics': {'cost': total_cost, 'conversions': total_conversions, 'value': total_value, 'roas': total_roas}, 'rows': df.fillna(0).sort_values(['conversion_value', 'cost'], ascending=[False, False]).to_dict(orient='records')}


def _google_ads_products_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.DataFrame(get_product_performance(date_range=f['adsDateRange']))
    if f['campaignFilter'].strip() and not df.empty:
        df = df[df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    if f['selectedItemId'] and not df.empty:
        df = df[df['product_item_id'].astype(str) == f['selectedItemId']]
    elif f['productFilter'].strip() and not df.empty:
        df = df[df['product_title'].astype(str).str.contains(f['productFilter'].strip(), case=False, na=False)]
    if df.empty:
        return {'metrics': {'cost': 0, 'clicks': 0, 'conversions': 0, 'value': 0, 'roas': 0}, 'rows': [], 'insights': []}

    for col in ['impressions', 'clicks', 'cost', 'conversions', 'conversion_value']:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['ctr'] = df.apply(lambda x: round((x['clicks'] / x['impressions']) * 100, 2) if x['impressions'] else 0, axis=1)
    df['cpa'] = df.apply(lambda x: round(x['cost'] / x['conversions'], 2) if x['conversions'] else 0, axis=1)
    df['roas'] = df.apply(lambda x: round(x['conversion_value'] / x['cost'], 2) if x['cost'] else 0, axis=1)

    total_cost = round(float(df['cost'].sum()), 2)
    total_clicks = round(float(df['clicks'].sum()), 2)
    total_conversions = round(float(df['conversions'].sum()), 2)
    total_value = round(float(df['conversion_value'].sum()), 2)
    total_roas = round(total_value / total_cost, 2) if total_cost else 0
    insights_df = generate_google_ads_product_insights(df)
    return {
        'metrics': {k: to_python_scalar(v) for k, v in {
            'cost': total_cost,
            'clicks': total_clicks,
            'conversions': total_conversions,
            'value': total_value,
            'roas': total_roas,
        }.items()},
        'rows': to_python_records(df.fillna(0).sort_values(['conversion_value', 'cost'], ascending=[False, False]).to_dict(orient='records')),
        'insights': to_python_records(insights_df.fillna(0).to_dict(orient='records')) if not insights_df.empty else []
    }


def _pmax_campaign_products_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    try:
        ads_date_range = f.get('adsDateRange', 'LAST_30_DAYS')
        campaign_filter = (f.get('campaignFilter') or '').strip().lower()
        product_filter = (f.get('productFilter') or '').strip().lower()
        selected_item_id = str(f.get('selectedItemId') or '').strip()
        pmax_campaign_name = (f.get('pmaxCampaignName') or '').strip()
        asset_group_name = (f.get('assetGroupName') or '').strip()
        compare_previous = bool(f.get('comparePrevious', False))

        base_rows = get_product_performance(date_range=ads_date_range, include_asset_group=True)
        df = pd.DataFrame(base_rows)
        pmax_campaign_names = _get_pmax_campaign_names(ads_date_range)

        def _prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
            if frame.empty:
                return frame
            rename_map = {}
            if 'product_name' in frame.columns and 'item_name' not in frame.columns:
                rename_map['product_name'] = 'item_name'
            if 'product_title' in frame.columns and 'item_name' not in frame.columns:
                rename_map['product_title'] = 'item_name'
            if 'product_item_id' in frame.columns and 'item_id' not in frame.columns:
                rename_map['product_item_id'] = 'item_id'
            if 'value' in frame.columns and 'conversion_value' not in frame.columns:
                rename_map['value'] = 'conversion_value'
            frame = frame.rename(columns=rename_map)

            required_defaults = {
                'campaign_name': '',
                'item_id': '',
                'item_name': '',
                'asset_group_id': '',
                'asset_group_name': '',
                'clicks': 0,
                'impressions': 0,
                'cost': 0,
                'conversions': 0,
                'conversion_value': 0,
            }
            for col, default in required_defaults.items():
                if col not in frame.columns:
                    frame[col] = default

            frame['campaign_name'] = frame['campaign_name'].fillna('').astype(str)
            frame['item_name'] = frame['item_name'].fillna('').astype(str)
            frame['item_id'] = frame['item_id'].fillna('').astype(str)
            frame['asset_group_name'] = frame['asset_group_name'].fillna('').astype(str)
            frame['asset_group_id'] = frame['asset_group_id'].fillna('').astype(str)
            frame = frame[frame['campaign_name'].isin(pmax_campaign_names)].copy()

            if pmax_campaign_name:
                frame = frame[frame['campaign_name'] == pmax_campaign_name].copy()
            if campaign_filter:
                frame = frame[frame['campaign_name'].str.lower().str.contains(campaign_filter, na=False)].copy()
            if product_filter:
                frame = frame[frame['item_name'].str.lower().str.contains(product_filter, na=False)].copy()
            if selected_item_id:
                frame = frame[frame['item_id'] == selected_item_id].copy()
            if asset_group_name:
                frame = frame[frame['asset_group_name'] == asset_group_name].copy()

            for col in ['clicks', 'impressions', 'cost', 'conversions', 'conversion_value']:
                frame[col] = pd.to_numeric(frame[col], errors='coerce').fillna(0)

            if frame.empty:
                return frame

            frame['ctr'] = np.where(frame['impressions'] > 0, (frame['clicks'] / frame['impressions']) * 100, 0)
            frame['cpc'] = np.where(frame['clicks'] > 0, frame['cost'] / frame['clicks'], 0)
            frame['cpa'] = np.where(frame['conversions'] > 0, frame['cost'] / frame['conversions'], 0)
            frame['roas'] = np.where(frame['cost'] > 0, frame['conversion_value'] / frame['cost'], 0)
            return frame

        df = _prepare_frame(df)
        asset_groups = sorted([x for x in df['asset_group_name'].dropna().astype(str).unique().tolist() if x]) if not df.empty else []

        def _build_payload(frame: pd.DataFrame) -> Dict[str, Any]:
            if frame.empty:
                return {
                    'metrics': {
                        'cost': 0.0,
                        'clicks': 0.0,
                        'conversions': 0.0,
                        'value': 0.0,
                        'roas': 0.0,
                        'campaign_count': 0,
                        'product_count': 0,
                        'asset_group_count': 0,
                    },
                    'rows': [],
                    'insights': [],
                    'asset_group_summary': [],
                }

            total_cost = round(float(frame['cost'].sum()), 2)
            total_clicks = round(float(frame['clicks'].sum()), 2)
            total_conversions = round(float(frame['conversions'].sum()), 2)
            total_value = round(float(frame['conversion_value'].sum()), 2)
            total_roas = round(total_value / total_cost, 2) if total_cost > 0 else 0.0
            campaign_count = int(frame['campaign_name'].nunique())
            product_count = int(frame['item_id'].astype(str).nunique()) if 'item_id' in frame.columns else len(frame)
            asset_group_count = int(frame['asset_group_name'].astype(str).replace('', np.nan).dropna().nunique()) if 'asset_group_name' in frame.columns else 0

            insights = []
            cost_no_conv = frame[(frame['cost'] > 0) & (frame['conversions'] <= 0)]
            for _, row in cost_no_conv.sort_values('cost', ascending=False).head(10).iterrows():
                insights.append({
                    'type': 'cost_without_conversions',
                    'campaign_name': row.get('campaign_name', ''),
                    'asset_group_name': row.get('asset_group_name', ''),
                    'item_id': str(row.get('item_id', '')),
                    'item_name': row.get('item_name', ''),
                    'cost': round(float(row.get('cost', 0)), 2),
                    'clicks': round(float(row.get('clicks', 0)), 2),
                    'conversions': round(float(row.get('conversions', 0)), 2),
                    'roas': round(float(row.get('roas', 0)), 2),
                    'message': 'Produsul consumă cost fără conversii.'
                })

            scalable = frame[(frame['conversions'] > 0) & (frame['roas'] >= 3)]
            for _, row in scalable.sort_values(['roas', 'conversion_value'], ascending=[False, False]).head(10).iterrows():
                insights.append({
                    'type': 'scalable_product',
                    'campaign_name': row.get('campaign_name', ''),
                    'asset_group_name': row.get('asset_group_name', ''),
                    'item_id': str(row.get('item_id', '')),
                    'item_name': row.get('item_name', ''),
                    'cost': round(float(row.get('cost', 0)), 2),
                    'clicks': round(float(row.get('clicks', 0)), 2),
                    'conversions': round(float(row.get('conversions', 0)), 2),
                    'roas': round(float(row.get('roas', 0)), 2),
                    'message': 'Produs cu ROAS bun, candidat pentru scalare.'
                })

            weak_ctr = frame[(frame['impressions'] > 1000) & (frame['ctr'] < 0.5)]
            for _, row in weak_ctr.sort_values('impressions', ascending=False).head(10).iterrows():
                insights.append({
                    'type': 'weak_ctr',
                    'campaign_name': row.get('campaign_name', ''),
                    'asset_group_name': row.get('asset_group_name', ''),
                    'item_id': str(row.get('item_id', '')),
                    'item_name': row.get('item_name', ''),
                    'impressions': round(float(row.get('impressions', 0)), 2),
                    'clicks': round(float(row.get('clicks', 0)), 2),
                    'ctr': round(float(row.get('ctr', 0)), 2),
                    'message': 'Produs cu impresii multe și CTR slab.'
                })

            asset_group_summary_df = (
                frame.groupby(['campaign_name', 'asset_group_name'], as_index=False)
                .agg(
                    cost=('cost', 'sum'),
                    clicks=('clicks', 'sum'),
                    impressions=('impressions', 'sum'),
                    conversions=('conversions', 'sum'),
                    conversion_value=('conversion_value', 'sum'),
                    products=('item_id', 'nunique'),
                )
                .sort_values(['conversion_value', 'cost'], ascending=[False, False])
            ) if 'asset_group_name' in frame.columns else pd.DataFrame()
            if not asset_group_summary_df.empty:
                asset_group_summary_df['ctr'] = np.where(asset_group_summary_df['impressions'] > 0, (asset_group_summary_df['clicks'] / asset_group_summary_df['impressions']) * 100, 0)
                asset_group_summary_df['cpc'] = np.where(asset_group_summary_df['clicks'] > 0, asset_group_summary_df['cost'] / asset_group_summary_df['clicks'], 0)
                asset_group_summary_df['cpa'] = np.where(asset_group_summary_df['conversions'] > 0, asset_group_summary_df['cost'] / asset_group_summary_df['conversions'], 0)
                asset_group_summary_df['roas'] = np.where(asset_group_summary_df['cost'] > 0, asset_group_summary_df['conversion_value'] / asset_group_summary_df['cost'], 0)

            rows_df = frame.sort_values(['conversion_value', 'cost'], ascending=[False, False]).copy()

            return {
                'metrics': {k: to_python_scalar(v) for k, v in {
                    'cost': total_cost,
                    'clicks': total_clicks,
                    'conversions': total_conversions,
                    'value': total_value,
                    'roas': total_roas,
                    'campaign_count': campaign_count,
                    'product_count': product_count,
                    'asset_group_count': asset_group_count,
                }.items()},
                'rows': to_python_records(rows_df.fillna(0).to_dict(orient='records')),
                'insights': to_python_records(insights),
                'asset_group_summary': to_python_records(asset_group_summary_df.fillna(0).to_dict(orient='records')) if not asset_group_summary_df.empty else [],
            }

        current_payload = _build_payload(df)

        response = {
            'campaigns': sorted([str(x) for x in pmax_campaign_names]),
            'asset_groups': asset_groups,
            'campaign_type': 'PERFORMANCE_MAX',
            'identification_method': 'channel_type',
            **current_payload,
        }

        if current_payload['rows'] == [] and pmax_campaign_names:
            response['error'] = 'Există campanii PERFORMANCE_MAX, dar nu am găsit produse pentru filtrele selectate.'
        elif not pmax_campaign_names:
            response['error'] = 'Nu am găsit campanii PERFORMANCE_MAX în Google Ads pentru intervalul selectat.'

        if compare_previous:
            prev_ads_range = get_previous_pmax_ads_preset(ads_date_range)
            if prev_ads_range:
                previous_rows = get_product_performance(date_range=prev_ads_range, include_asset_group=True)
                prev_df = _prepare_frame(pd.DataFrame(previous_rows))
                previous_payload = _build_payload(prev_df)
                current_metrics = current_payload.get('metrics', {})
                previous_metrics = previous_payload.get('metrics', {})
                metric_keys = ['cost', 'clicks', 'conversions', 'value', 'roas', 'product_count']
                response['comparison'] = {
                    'available': True,
                    'current_ads_range': ads_date_range,
                    'previous_ads_range': prev_ads_range,
                    'previous_metrics': {k: to_python_scalar(previous_metrics.get(k, 0)) for k in metric_keys},
                    'metric_deltas': {k: _build_metric_delta(current_metrics.get(k, 0), previous_metrics.get(k, 0)) for k in metric_keys},
                }
            else:
                response['comparison'] = {
                    'available': False,
                    'current_ads_range': ads_date_range,
                    'previous_ads_range': '',
                    'previous_metrics': {},
                    'metric_deltas': {},
                }

        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'campaigns': [],
            'asset_groups': [],
            'metrics': {
                'cost': 0.0,
                'clicks': 0.0,
                'conversions': 0.0,
                'value': 0.0,
                'roas': 0.0,
                'campaign_count': 0,
                'product_count': 0,
                'asset_group_count': 0,
            },
            'rows': [],
            'insights': [],
            'asset_group_summary': [],
            'campaign_type': 'PERFORMANCE_MAX',
            'identification_method': 'channel_type',
            'error': f'Eroare la încărcarea produselor PMAX: {str(e)}',
        }

def _meta_campaigns_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.DataFrame(get_meta_campaign_performance(date_preset=f['metaDateRange']))
    if f['campaignFilter'].strip() and not df.empty:
        df = df[df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    if df.empty:
        return {'metrics': {'spend': 0, 'purchases': 0, 'value': 0, 'roas': 0}, 'rows': []}
    df['ctr'] = df.apply(lambda x: round((x['clicks'] / x['impressions']) * 100, 2) if x['impressions'] else 0, axis=1)
    df['cpc'] = df.apply(lambda x: round(x['spend'] / x['clicks'], 2) if x['clicks'] else 0, axis=1)
    df['cpa'] = df.apply(lambda x: round(x['spend'] / x['purchases'], 2) if x['purchases'] else 0, axis=1)
    df['roas'] = df.apply(lambda x: round(x['purchase_value'] / x['spend'], 2) if x['spend'] else 0, axis=1)
    total_spend = round(df['spend'].sum(), 2)
    total_purchases = round(df['purchases'].sum(), 2)
    total_value = round(df['purchase_value'].sum(), 2)
    total_roas = round(total_value / total_spend, 2) if total_spend else 0
    return {'metrics': {'spend': total_spend, 'purchases': total_purchases, 'value': total_value, 'roas': total_roas}, 'rows': df.fillna(0).sort_values(['purchase_value', 'spend'], ascending=[False, False]).to_dict(orient='records')}


def _meta_adsets_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.DataFrame(get_meta_adset_performance(date_preset=f['metaDateRange']))
    if f['campaignFilter'].strip() and not df.empty:
        df = df[df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    if df.empty:
        return {'metrics': {'spend': 0, 'purchases': 0, 'value': 0, 'roas': 0}, 'rows': []}
    df['ctr'] = df.apply(lambda x: round((x['clicks'] / x['impressions']) * 100, 2) if x['impressions'] else 0, axis=1)
    df['cpc'] = df.apply(lambda x: round(x['spend'] / x['clicks'], 2) if x['clicks'] else 0, axis=1)
    df['cpa'] = df.apply(lambda x: round(x['spend'] / x['purchases'], 2) if x['purchases'] else 0, axis=1)
    df['roas'] = df.apply(lambda x: round(x['purchase_value'] / x['spend'], 2) if x['spend'] else 0, axis=1)
    total_spend = round(df['spend'].sum(), 2)
    total_purchases = round(df['purchases'].sum(), 2)
    total_value = round(df['purchase_value'].sum(), 2)
    total_roas = round(total_value / total_spend, 2) if total_spend else 0
    return {'metrics': {'spend': total_spend, 'purchases': total_purchases, 'value': total_value, 'roas': total_roas}, 'rows': df.fillna(0).sort_values(['purchase_value', 'spend'], ascending=[False, False]).to_dict(orient='records')}


def _meta_products_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.DataFrame(get_meta_product_performance(date_preset=f['metaDateRange']))
    if f['campaignFilter'].strip() and not df.empty:
        df = df[df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    if f['selectedItemId'] and not df.empty:
        df = df[df['product_id'].astype(str).str.contains(f['selectedItemId'], case=False, na=False)]
    elif f['productFilter'].strip() and not df.empty:
        df = df[df['product_id'].astype(str).str.contains(f['productFilter'].strip(), case=False, na=False)]
    if df.empty:
        return {'metrics': {'spend': 0, 'view_content': 0, 'add_to_cart': 0, 'cpc': 0}, 'rows': []}
    df['ctr'] = df.apply(lambda x: round((x['clicks'] / x['impressions']) * 100, 2) if x['impressions'] else 0, axis=1)
    df['cpc'] = df.apply(lambda x: round(x['spend'] / x['clicks'], 2) if x['clicks'] else 0, axis=1)
    df['view_to_atc_rate'] = df.apply(lambda x: round((x['add_to_cart'] / x['view_content']) * 100, 2) if x['view_content'] else 0, axis=1)
    total_spend = round(df['spend'].sum(), 2)
    total_view_content = int(df['view_content'].sum())
    total_add_to_cart = int(df['add_to_cart'].sum())
    total_clicks = df['clicks'].sum()
    total_cpc = round(total_spend / total_clicks, 2) if total_clicks else 0
    return {'metrics': {'spend': total_spend, 'view_content': total_view_content, 'add_to_cart': total_add_to_cart, 'cpc': total_cpc}, 'rows': df.fillna(0).sort_values(['spend', 'view_content'], ascending=[False, False]).to_dict(orient='records')}


def _ga4_products_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    response = get_product_funnel_report_with_id(start_date=f['ga4Start'], end_date=f['ga4End'])
    rows = []
    for row in response.rows:
        rows.append({'item_id': row.dimension_values[0].value, 'item_name': row.dimension_values[1].value, 'items_viewed': int(row.metric_values[0].value), 'items_added_to_cart': int(row.metric_values[1].value), 'items_purchased': int(row.metric_values[2].value), 'item_revenue': float(row.metric_values[3].value)})
    df = pd.DataFrame(rows)
    if f['selectedItemId'] and not df.empty:
        df = df[df['item_id'].astype(str) == f['selectedItemId']]
    elif f['productFilter'].strip() and not df.empty:
        df = df[df['item_name'].astype(str).str.contains(f['productFilter'].strip(), case=False, na=False)]
    if df.empty:
        return {'metrics': {'views': 0, 'add_to_cart': 0, 'purchases': 0, 'revenue': 0}, 'rows': []}
    df['view_to_atc_rate'] = df.apply(lambda x: round((x['items_added_to_cart'] / x['items_viewed']) * 100, 2) if x['items_viewed'] else 0, axis=1)
    df['purchase_rate'] = df.apply(lambda x: round((x['items_purchased'] / x['items_viewed']) * 100, 2) if x['items_viewed'] else 0, axis=1)
    return {'metrics': {'views': int(df['items_viewed'].sum()), 'add_to_cart': int(df['items_added_to_cart'].sum()), 'purchases': int(df['items_purchased'].sum()), 'revenue': round(df['item_revenue'].sum(), 2)}, 'rows': df.fillna(0).sort_values(['item_revenue', 'items_viewed'], ascending=[False, False]).to_dict(orient='records')}


def _ga4_traffic_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    response = get_traffic_campaign_report(start_date=f['ga4Start'], end_date=f['ga4End'])
    rows = []
    for row in response.rows:
        rows.append({'source_medium': row.dimension_values[0].value, 'campaign_name': row.dimension_values[1].value, 'sessions': int(row.metric_values[0].value), 'engaged_sessions': int(row.metric_values[1].value), 'purchases': int(row.metric_values[2].value), 'purchase_revenue': float(row.metric_values[3].value)})
    df = pd.DataFrame(rows)
    if f['trafficType'] == 'paid only':
        df = df[df['source_medium'].astype(str).str.contains('cpc|ppc|paid', case=False, na=False)]
    elif f['trafficType'] == 'google / cpc only':
        df = df[df['source_medium'].astype(str).str.contains('google / cpc', case=False, na=False)]
    if f['campaignFilter'].strip() and not df.empty:
        df = df[df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    if df.empty:
        return {'metrics': {'sessions': 0, 'engaged_sessions': 0, 'purchases': 0, 'revenue': 0}, 'rows': []}
    df = _add_session_rates(df)
    return {'metrics': {'sessions': int(df['sessions'].sum()), 'engaged_sessions': int(df['engaged_sessions'].sum()), 'purchases': int(df['purchases'].sum()), 'revenue': round(df['purchase_revenue'].sum(), 2)}, 'rows': df.fillna(0).sort_values(['purchase_revenue', 'sessions'], ascending=[False, False]).to_dict(orient='records')}


def _landing_pages_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    response = get_landing_page_conversion_report(start_date=f['ga4Start'], end_date=f['ga4End'])
    rows = []
    for row in response.rows:
        rows.append({'landing_page': row.dimension_values[0].value, 'sessions': int(row.metric_values[0].value), 'engaged_sessions': int(row.metric_values[1].value), 'purchases': int(row.metric_values[2].value), 'purchase_revenue': float(row.metric_values[3].value)})
    df = pd.DataFrame(rows)
    if f['pageType'] == 'produse (/p/)':
        df = df[df['landing_page'].astype(str).str.startswith('/p/', na=False)]
    elif f['pageType'] == 'categorii (/c/)':
        df = df[df['landing_page'].astype(str).str.startswith('/c/', na=False)]
    if df.empty:
        return {'metrics': {'sessions': 0, 'engaged_sessions': 0, 'purchases': 0, 'revenue': 0}, 'rows': []}
    df = _add_session_rates(df)
    return {'metrics': {'sessions': int(df['sessions'].sum()), 'engaged_sessions': int(df['engaged_sessions'].sum()), 'purchases': int(df['purchases'].sum()), 'revenue': round(df['purchase_revenue'].sum(), 2)}, 'rows': df.fillna(0).sort_values(['purchase_revenue', 'sessions'], ascending=[False, False]).to_dict(orient='records')}


def _devices_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    response = get_device_report(start_date=f['ga4Start'], end_date=f['ga4End'])
    rows = []
    for row in response.rows:
        rows.append({'device': row.dimension_values[0].value, 'sessions': int(row.metric_values[0].value), 'engaged_sessions': int(row.metric_values[1].value), 'purchase_revenue': float(row.metric_values[2].value), 'purchases': int(row.metric_values[3].value)})
    df = pd.DataFrame(rows)
    if df.empty:
        return {'metrics': {'sessions': 0, 'engaged_sessions': 0, 'purchases': 0, 'revenue': 0}, 'rows': []}
    df = _add_session_rates(df)
    return {'metrics': {'sessions': int(df['sessions'].sum()), 'engaged_sessions': int(df['engaged_sessions'].sum()), 'purchases': int(df['purchases'].sum()), 'revenue': round(df['purchase_revenue'].sum(), 2)}, 'rows': df.fillna(0).sort_values(['purchase_revenue', 'sessions'], ascending=[False, False]).to_dict(orient='records')}


def _product_channels_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    response = get_product_source_medium_performance_report(start_date=f['ga4Start'], end_date=f['ga4End'])
    rows = []
    for row in response.rows:
        rows.append({'item_id': row.dimension_values[0].value, 'item_name': row.dimension_values[1].value, 'source_medium': row.dimension_values[2].value, 'items_viewed': int(row.metric_values[0].value), 'items_added_to_cart': int(row.metric_values[1].value), 'items_purchased': int(row.metric_values[2].value), 'item_revenue': float(row.metric_values[3].value)})
    df = pd.DataFrame(rows)
    if f['selectedItemId'] and not df.empty:
        df = df[df['item_id'].astype(str) == f['selectedItemId']]
    elif f['productFilter'].strip() and not df.empty:
        df = df[df['item_name'].astype(str).str.contains(f['productFilter'].strip(), case=False, na=False)]
    if f['sourceFilter'].strip() and not df.empty:
        df = df[df['source_medium'].astype(str).str.contains(f['sourceFilter'].strip(), case=False, na=False)]
    if df.empty:
        return {'metrics': {'views': 0, 'add_to_cart': 0, 'purchases': 0, 'revenue': 0}, 'rows': []}
    grouped = df.groupby('source_medium', as_index=False).agg({'items_viewed': 'sum', 'items_added_to_cart': 'sum', 'items_purchased': 'sum', 'item_revenue': 'sum'})
    grouped = _add_product_rates(grouped)
    grouped['revenue_per_view'] = grouped.apply(lambda x: round(x['item_revenue'] / x['items_viewed'], 2) if x['items_viewed'] else 0, axis=1)
    return {'metrics': {'views': int(grouped['items_viewed'].sum()), 'add_to_cart': int(grouped['items_added_to_cart'].sum()), 'purchases': int(grouped['items_purchased'].sum()), 'revenue': round(grouped['item_revenue'].sum(), 2)}, 'rows': grouped.fillna(0).sort_values(['item_revenue', 'items_viewed'], ascending=[False, False]).to_dict(orient='records')}


def _join_ads_ga4_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    ads_df = pd.DataFrame(get_product_performance(date_range=f['adsDateRange']))
    ga4_response = get_product_source_report_with_id(start_date=f['ga4Start'], end_date=f['ga4End'])
    ga4_rows = []
    for row in ga4_response.rows:
        ga4_rows.append({'item_id': row.dimension_values[0].value, 'item_name': row.dimension_values[1].value, 'source_medium': row.dimension_values[2].value, 'items_viewed': int(row.metric_values[0].value), 'items_added_to_cart': int(row.metric_values[1].value), 'items_purchased': int(row.metric_values[2].value), 'item_revenue': float(row.metric_values[3].value)})
    ga4_df = pd.DataFrame(ga4_rows)
    if f['campaignFilter'].strip() and not ads_df.empty:
        ads_df = ads_df[ads_df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    if f['selectedItemId']:
        if not ads_df.empty:
            ads_df = ads_df[ads_df['product_item_id'].astype(str) == f['selectedItemId']]
        if not ga4_df.empty:
            ga4_df = ga4_df[ga4_df['item_id'].astype(str) == f['selectedItemId']]
    elif f['productFilter'].strip():
        if not ads_df.empty:
            ads_df = ads_df[ads_df['product_title'].astype(str).str.contains(f['productFilter'].strip(), case=False, na=False)]
        if not ga4_df.empty:
            ga4_df = ga4_df[ga4_df['item_name'].astype(str).str.contains(f['productFilter'].strip(), case=False, na=False)]
    report_df = add_product_status(build_main_product_report(ads_df, ga4_df))
    insights_df = generate_main_product_report_insights(report_df)
    metrics = {'products': int(len(report_df)), 'problematic': int((report_df['status'] == '🔴 Problematic').sum()) if not report_df.empty else 0, 'attention': int((report_df['status'] == '🟠 Atenție').sum()) if not report_df.empty else 0, 'good': int((report_df['status'] == '🟢 Bun').sum()) if not report_df.empty else 0}
    return {'metrics': metrics, 'rows': report_df.fillna(0).to_dict(orient='records') if not report_df.empty else [], 'insights': insights_df.fillna(0).to_dict(orient='records') if not insights_df.empty else []}


def _pmax_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    campaign_df = pd.DataFrame(get_campaign_performance(date_range=f['adsDateRange']))
    product_df = pd.DataFrame(get_product_performance(date_range=f['adsDateRange']))
    if not campaign_df.empty:
        campaign_df = campaign_df[campaign_df['channel_type'].astype(int) == 10]
    if not product_df.empty and not campaign_df.empty:
        valid_campaign_ids = campaign_df['campaign_id'].astype(str).tolist()
        product_df = product_df[product_df['campaign_id'].astype(str).isin(valid_campaign_ids)]
    if f['campaignFilter'].strip() and not campaign_df.empty:
        campaign_df = campaign_df[campaign_df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    if f['campaignFilter'].strip() and not product_df.empty:
        product_df = product_df[product_df['campaign_name'].astype(str).str.contains(f['campaignFilter'].strip(), case=False, na=False)]
    report_df = build_pmax_feed_vs_other_report(campaign_df, product_df)
    total_clicks = int(report_df['total_clicks'].sum()) if not report_df.empty else 0
    product_clicks = int(report_df['product_clicks_estimate'].sum()) if not report_df.empty else 0
    other_clicks = int(report_df['other_clicks_estimate'].sum()) if not report_df.empty else 0
    feed_share = round((product_clicks / total_clicks) * 100, 2) if total_clicks else 0
    totals_df = add_totals_row(report_df) if not report_df.empty else pd.DataFrame()
    return {'metrics': {'total_clicks': total_clicks, 'product_clicks': product_clicks, 'other_clicks': other_clicks, 'feed_share': feed_share}, 'rows': report_df.fillna(0).to_dict(orient='records') if not report_df.empty else [], 'totals': totals_df.fillna(0).to_dict(orient='records') if not totals_df.empty else []}


def _favi_impl(f: Dict[str, Any]) -> Dict[str, Any]:
    overview_response = get_favi_overview_report(start_date=f['ga4Start'], end_date=f['ga4End'])
    product_response = get_favi_product_report(start_date=f['ga4Start'], end_date=f['ga4End'])
    landing_response = get_favi_landing_pages_report(start_date=f['ga4Start'], end_date=f['ga4End'])
    device_response = get_favi_device_report(start_date=f['ga4Start'], end_date=f['ga4End'])
    overview_rows = []
    for row in overview_response.rows:
        overview_rows.append({'source_medium': row.dimension_values[0].value, 'sessions': int(row.metric_values[0].value), 'engaged_sessions': int(row.metric_values[1].value), 'purchases': int(row.metric_values[2].value), 'purchase_revenue': float(row.metric_values[3].value)})
    overview_df = _add_session_rates(pd.DataFrame(overview_rows))
    overview_metrics = {'sessions': 0, 'purchases': 0, 'revenue': 0, 'purchase_rate': 0, 'engaged_sessions': 0, 'engagement_rate': 0, 'revenue_per_session': 0}
    if not overview_df.empty:
        o = overview_df.iloc[0]
        overview_metrics = {'sessions': int(o['sessions']), 'purchases': int(o['purchases']), 'revenue': round(float(o['purchase_revenue']), 2), 'purchase_rate': round(float(o.get('purchase_rate', 0)), 2), 'engaged_sessions': int(o['engaged_sessions']), 'engagement_rate': round(float(o.get('engagement_rate', 0)), 2), 'revenue_per_session': round(float(o.get('revenue_per_session', 0)), 2)}
    product_rows = []
    for row in product_response.rows:
        product_rows.append({'item_id': row.dimension_values[0].value, 'item_name': row.dimension_values[1].value, 'items_viewed': int(row.metric_values[0].value), 'items_added_to_cart': int(row.metric_values[1].value), 'items_purchased': int(row.metric_values[2].value), 'item_revenue': float(row.metric_values[3].value)})
    products_df = pd.DataFrame(product_rows)
    if f['selectedItemId'] and not products_df.empty:
        products_df = products_df[products_df['item_id'].astype(str) == str(f['selectedItemId'])]
    elif f['productFilter'].strip() and not products_df.empty:
        products_df = products_df[products_df['item_name'].astype(str).str.contains(f['productFilter'].strip(), case=False, na=False)]
    products_df = _add_product_rates(products_df)
    products_df = products_df.sort_values(['item_revenue', 'items_purchased'], ascending=False) if not products_df.empty else products_df
    weak_df = pd.DataFrame()
    if not products_df.empty:
        weak_df = products_df[(products_df['items_viewed'] >= 20) & (products_df['view_to_purchase_rate'] <= 1.0)].copy()
        weak_df = weak_df.sort_values(['items_viewed', 'item_revenue'], ascending=[False, True]).head(10)
    landing_rows = []
    for row in landing_response.rows:
        landing_rows.append({'landing_page': row.dimension_values[0].value, 'sessions': int(row.metric_values[0].value), 'engaged_sessions': int(row.metric_values[1].value), 'purchases': int(row.metric_values[2].value), 'purchase_revenue': float(row.metric_values[3].value)})
    landing_df = pd.DataFrame(landing_rows)
    if f['pageType'] == 'produse (/p/)':
        landing_df = landing_df[landing_df['landing_page'].astype(str).str.startswith('/p/', na=False)]
    elif f['pageType'] == 'categorii (/c/)':
        landing_df = landing_df[landing_df['landing_page'].astype(str).str.startswith('/c/', na=False)]
    landing_df = _add_session_rates(landing_df)
    landing_df = landing_df.sort_values(['purchase_revenue', 'sessions'], ascending=False) if not landing_df.empty else landing_df
    device_rows = []
    for row in device_response.rows:
        device_rows.append({'device': row.dimension_values[0].value, 'sessions': int(row.metric_values[0].value), 'engaged_sessions': int(row.metric_values[1].value), 'purchases': int(row.metric_values[2].value), 'purchase_revenue': float(row.metric_values[3].value)})
    device_df = _add_session_rates(pd.DataFrame(device_rows))
    device_df = device_df.sort_values('purchase_revenue', ascending=False) if not device_df.empty else device_df
    return {'source_medium': FAVI_SOURCE_MEDIUM, 'overview': overview_metrics, 'products': products_df.fillna(0).to_dict(orient='records') if not products_df.empty else [], 'product_opportunities': weak_df.fillna(0).to_dict(orient='records') if not weak_df.empty else [], 'landing_pages': landing_df.fillna(0).to_dict(orient='records') if not landing_df.empty else [], 'devices': device_df.fillna(0).to_dict(orient='records') if not device_df.empty else []}


HANDLERS = {
    'get_overview': _overview_impl,
    'get_google_ads_campaigns': _google_ads_campaigns_impl,
    'get_google_ads_products': _google_ads_products_impl,
    'get_meta_campaigns': _meta_campaigns_impl,
    'get_meta_adsets': _meta_adsets_impl,
    'get_meta_products': _meta_products_impl,
    'get_ga4_products': _ga4_products_impl,
    'get_ga4_traffic': _ga4_traffic_impl,
    'get_landing_pages': _landing_pages_impl,
    'get_ga4_devices': _devices_impl,
    'get_product_channels': _product_channels_impl,
    'get_join_ads_ga4': _join_ads_ga4_impl,
    'get_pmax_feed_vs_other': _pmax_impl,
    'get_favi_report': _favi_impl,
}

copilot_service = CopilotService(HANDLERS)


@app.get('/health')
def health() -> Dict[str, str]:
    return {'status': 'ok'}


@app.get('/api/ai/providers')
def ai_providers() -> list[dict]:
    return copilot_service.provider_catalog()


@app.post('/api/copilot/chat')
def copilot_chat(request: CopilotRequest) -> dict[str, Any]:
    return copilot_service.chat(request)



@app.get('/api/overview')
def overview_endpoint(ga4_start: str = '30daysAgo', ga4_end: str = 'today', ads_date_range: str = 'LAST_30_DAYS', meta_date_preset: str = 'last_30d', campaign_filter: str = '', product_filter: str = '', selected_item_id: str = '', compare_previous: str = 'false') -> Dict[str, Any]:
    return _overview_impl({'ga4Start': ga4_start, 'ga4End': ga4_end, 'adsDateRange': ads_date_range, 'metaDateRange': meta_date_preset, 'campaignFilter': campaign_filter, 'productFilter': product_filter, 'selectedItemId': selected_item_id, 'comparePrevious': str(compare_previous).lower() == 'true'})


@app.get('/api/google-ads/campaigns')
def google_ads_campaigns_endpoint(ads_date_range: str = 'LAST_30_DAYS', campaign_filter: str = '') -> Dict[str, Any]:
    return _google_ads_campaigns_impl({'adsDateRange': ads_date_range, 'campaignFilter': campaign_filter})


@app.get('/api/google-ads/products')
def google_ads_products_endpoint(ads_date_range: str = 'LAST_30_DAYS', campaign_filter: str = '', product_filter: str = '', selected_item_id: str = '') -> Dict[str, Any]:
    return _google_ads_products_impl({'adsDateRange': ads_date_range, 'campaignFilter': campaign_filter, 'productFilter': product_filter, 'selectedItemId': selected_item_id})


@app.get('/api/google-ads/pmax-campaign-products')
def google_ads_pmax_campaign_products_endpoint(ads_date_range: str = 'LAST_30_DAYS', campaign_filter: str = '', product_filter: str = '', selected_item_id: str = '', pmax_campaign: str = '', asset_group: str = '', compare_previous: str = 'false') -> Dict[str, Any]:
    return _pmax_campaign_products_impl({'adsDateRange': ads_date_range, 'campaignFilter': campaign_filter, 'productFilter': product_filter, 'selectedItemId': selected_item_id, 'pmaxCampaignName': pmax_campaign, 'assetGroupName': asset_group, 'comparePrevious': str(compare_previous).lower() == 'true'})


@app.get('/api/meta/campaigns')
def meta_campaigns_endpoint(meta_date_preset: str = 'last_30d', campaign_filter: str = '') -> Dict[str, Any]:
    return _meta_campaigns_impl({'metaDateRange': meta_date_preset, 'campaignFilter': campaign_filter})


@app.get('/api/meta/adsets')
def meta_adsets_endpoint(meta_date_preset: str = 'last_30d', campaign_filter: str = '') -> Dict[str, Any]:
    return _meta_adsets_impl({'metaDateRange': meta_date_preset, 'campaignFilter': campaign_filter})


@app.get('/api/meta/products')
def meta_products_endpoint(meta_date_preset: str = 'last_30d', campaign_filter: str = '', product_filter: str = '', selected_item_id: str = '') -> Dict[str, Any]:
    return _meta_products_impl({'metaDateRange': meta_date_preset, 'campaignFilter': campaign_filter, 'productFilter': product_filter, 'selectedItemId': selected_item_id})


@app.get('/api/ga4/products')
def ga4_products_endpoint(ga4_start: str = '30daysAgo', ga4_end: str = 'today', product_filter: str = '', selected_item_id: str = '') -> Dict[str, Any]:
    return _ga4_products_impl({'ga4Start': ga4_start, 'ga4End': ga4_end, 'productFilter': product_filter, 'selectedItemId': selected_item_id})


@app.get('/api/ga4/traffic')
def ga4_traffic_endpoint(ga4_start: str = '30daysAgo', ga4_end: str = 'today', traffic_type: str = 'toate', campaign_filter: str = '') -> Dict[str, Any]:
    return _ga4_traffic_impl({'ga4Start': ga4_start, 'ga4End': ga4_end, 'trafficType': traffic_type, 'campaignFilter': campaign_filter})


@app.get('/api/ga4/landing-pages')
def ga4_landing_pages_endpoint(ga4_start: str = '30daysAgo', ga4_end: str = 'today', page_type: str = 'toate') -> Dict[str, Any]:
    return _landing_pages_impl({'ga4Start': ga4_start, 'ga4End': ga4_end, 'pageType': page_type})


@app.get('/api/ga4/devices')
def ga4_devices_endpoint(ga4_start: str = '30daysAgo', ga4_end: str = 'today') -> Dict[str, Any]:
    return _devices_impl({'ga4Start': ga4_start, 'ga4End': ga4_end})


@app.get('/api/ga4/product-channels')
def ga4_product_channels_endpoint(ga4_start: str = '30daysAgo', ga4_end: str = 'today', source_filter: str = '', product_filter: str = '', selected_item_id: str = '') -> Dict[str, Any]:
    return _product_channels_impl({'ga4Start': ga4_start, 'ga4End': ga4_end, 'sourceFilter': source_filter, 'productFilter': product_filter, 'selectedItemId': selected_item_id})


@app.get('/api/join-ads-ga4')
def join_ads_ga4_endpoint(ga4_start: str = '30daysAgo', ga4_end: str = 'today', ads_date_range: str = 'LAST_30_DAYS', campaign_filter: str = '', product_filter: str = '', selected_item_id: str = '') -> Dict[str, Any]:
    return _join_ads_ga4_impl({'ga4Start': ga4_start, 'ga4End': ga4_end, 'adsDateRange': ads_date_range, 'campaignFilter': campaign_filter, 'productFilter': product_filter, 'selectedItemId': selected_item_id})


@app.get('/api/pmax-feed-vs-other')
def pmax_feed_vs_other_endpoint(ads_date_range: str = 'LAST_30_DAYS', campaign_filter: str = '') -> Dict[str, Any]:
    return _pmax_impl({'adsDateRange': ads_date_range, 'campaignFilter': campaign_filter})


@app.get('/api/favi')
def favi_endpoint(ga4_start: str = '30daysAgo', ga4_end: str = 'today', product_filter: str = '', selected_item_id: str = '', page_type: str = 'toate') -> Dict[str, Any]:
    return _favi_impl({'ga4Start': ga4_start, 'ga4End': ga4_end, 'productFilter': product_filter, 'selectedItemId': selected_item_id, 'pageType': page_type})


@app.get('/api/funnel/coverage')
def funnel_coverage_endpoint(ads_date_range: str = 'LAST_30_DAYS', meta_date_preset: str = 'last_30d', campaign_filter: str = '', compare_previous: str = 'false') -> Dict[str, Any]:
    return _funnel_coverage_impl({
        'adsDateRange': ads_date_range,
        'metaDateRange': meta_date_preset,
        'campaignFilter': campaign_filter,
        'comparePrevious': str(compare_previous).lower() == 'true',
    })
