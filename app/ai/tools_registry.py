from __future__ import annotations

from typing import Any, Dict


def build_tool_specs() -> list[dict[str, Any]]:
    return [
        {
            'type': 'function',
            'name': name,
            'description': desc,
            'parameters': {
                'type': 'object',
                'properties': {
                    'campaignFilter': {'type': 'string'},
                    'productFilter': {'type': 'string'},
                    'selectedItemId': {'type': 'string'},
                    'trafficType': {'type': 'string'},
                    'pageType': {'type': 'string'},
                    'sourceFilter': {'type': 'string'},
                },
                'additionalProperties': False,
            },
        }
        for name, desc in [
            ('get_overview', 'Get the executive overview metrics and key product tables.'),
            ('get_google_ads_campaigns', 'Get Google Ads campaign performance.'),
            ('get_google_ads_products', 'Get Google Ads product performance and insights.'),
            ('get_meta_campaigns', 'Get Meta campaign performance.'),
            ('get_meta_adsets', 'Get Meta ad set performance.'),
            ('get_meta_products', 'Get Meta product performance.'),
            ('get_ga4_products', 'Get GA4 product performance.'),
            ('get_ga4_traffic', 'Get GA4 traffic and campaign performance.'),
            ('get_landing_pages', 'Get GA4 landing pages performance.'),
            ('get_ga4_devices', 'Get GA4 device performance.'),
            ('get_product_channels', 'Get product performance by source/medium.'),
            ('get_join_ads_ga4', 'Get the joined Ads + GA4 product report and insights.'),
            ('get_pmax_feed_vs_other', 'Get PMAX feed vs other estimates.'),
            ('get_favi_report', 'Get the dedicated FAVI report including overview, products, landing pages, and devices.'),
        ]
    ]


def default_filters(filters: Dict[str, Any] | None) -> Dict[str, Any]:
    base = {
        'ga4Start': '30daysAgo',
        'ga4End': 'today',
        'adsDateRange': 'LAST_30_DAYS',
        'metaDateRange': 'last_30d',
        'campaignFilter': '',
        'productFilter': '',
        'selectedItemId': '',
        'trafficType': 'toate',
        'pageType': 'toate',
        'sourceFilter': '',
    }
    base.update(filters or {})
    return base


def resolve_tool(name: str, filters: Dict[str, Any], args: Dict[str, Any], handlers: Dict[str, Any]) -> Dict[str, Any]:
    current = default_filters(filters)
    current.update({k: v for k, v in (args or {}).items() if v not in [None, '']})
    handler = handlers[name]
    return handler(current)
