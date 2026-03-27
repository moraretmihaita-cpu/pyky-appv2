from google.ads.googleads.client import GoogleAdsClient

from app.config import (
    GOOGLE_ADS_DEVELOPER_TOKEN,
    GOOGLE_ADS_CLIENT_ID,
    GOOGLE_ADS_CLIENT_SECRET,
    GOOGLE_ADS_REFRESH_TOKEN,
    GOOGLE_ADS_LOGIN_CUSTOMER_ID,
)


def get_google_ads_client():
    config = {
        "developer_token": GOOGLE_ADS_DEVELOPER_TOKEN,
        "client_id": GOOGLE_ADS_CLIENT_ID,
        "client_secret": GOOGLE_ADS_CLIENT_SECRET,
        "refresh_token": GOOGLE_ADS_REFRESH_TOKEN,
        "use_proto_plus": True,
    }

    if GOOGLE_ADS_LOGIN_CUSTOMER_ID:
        config["login_customer_id"] = GOOGLE_ADS_LOGIN_CUSTOMER_ID

    return GoogleAdsClient.load_from_dict(config)

from app.config import GOOGLE_ADS_CUSTOMER_ID
from datetime import date, timedelta



def get_campaign_performance(date_range="LAST_30_DAYS", date_filter=None):
    client = get_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")

    if date_filter is None:
        date_filter = f"segments.date DURING {date_range}"

    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          campaign.advertising_channel_type,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value
        FROM campaign
        WHERE {date_filter}
        ORDER BY metrics.clicks DESC
        LIMIT 1000
    """

    response = ga_service.search(
        customer_id=GOOGLE_ADS_CUSTOMER_ID,
        query=query,
    )

    rows = []
    for row in response:
        rows.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "channel_type": row.campaign.advertising_channel_type,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost": row.metrics.cost_micros / 1_000_000,
            "conversions": row.metrics.conversions,
            "conversion_value": row.metrics.conversions_value,
        })

    return rows



def get_product_performance(date_range="LAST_30_DAYS", date_filter=None):
    client = get_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")

    if date_filter is None:
        date_filter = f"segments.date DURING {date_range}"

    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          segments.product_item_id,
          segments.product_title,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value
        FROM shopping_performance_view
        WHERE {date_filter}
        ORDER BY metrics.clicks DESC
        LIMIT 500
    """

    response = ga_service.search(
        customer_id=GOOGLE_ADS_CUSTOMER_ID,
        query=query,
    )

    rows = []
    for row in response:
        rows.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "product_item_id": row.segments.product_item_id,
            "product_title": row.segments.product_title,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost": row.metrics.cost_micros / 1_000_000,
            "conversions": row.metrics.conversions,
            "conversion_value": row.metrics.conversions_value,
        })

    return rows


def get_previous_ads_query_filter(current_range):
    if current_range == "LAST_7_DAYS":
        today = date.today()
        end_prev = today - timedelta(days=8)
        start_prev = today - timedelta(days=14)
        return f"segments.date BETWEEN '{start_prev.isoformat()}' AND '{end_prev.isoformat()}'"

    if current_range == "LAST_30_DAYS":
        today = date.today()
        end_prev = today - timedelta(days=31)
        start_prev = today - timedelta(days=60)
        return f"segments.date BETWEEN '{start_prev.isoformat()}' AND '{end_prev.isoformat()}'"

    if current_range == "THIS_MONTH":
        return "segments.date DURING LAST_MONTH"

    if current_range == "LAST_MONTH":
        return "segments.date DURING LAST_MONTH"

    return "segments.date DURING LAST_30_DAYS"


def get_asset_group_performance(date_range="LAST_30_DAYS", date_filter=None, campaign_name=None):
    client = get_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")

    if date_filter is None:
        date_filter = f"segments.date DURING {date_range}"

    campaign_clause = ""
    if campaign_name:
        safe_campaign_name = str(campaign_name).replace("'", "\'")
        campaign_clause = f"\n          AND campaign.name = '{safe_campaign_name}'"

    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          campaign.advertising_channel_type,
          asset_group.id,
          asset_group.name,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value
        FROM asset_group
        WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
          AND {date_filter}{campaign_clause}
        ORDER BY metrics.conversions DESC, metrics.conversions_value DESC, metrics.clicks DESC
        LIMIT 1000
    """

    response = ga_service.search(
        customer_id=GOOGLE_ADS_CUSTOMER_ID,
        query=query,
    )

    rows = []
    for row in response:
        rows.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "channel_type": row.campaign.advertising_channel_type,
            "asset_group_id": row.asset_group.id,
            "asset_group_name": row.asset_group.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost": row.metrics.cost_micros / 1_000_000,
            "conversions": row.metrics.conversions,
            "conversion_value": row.metrics.conversions_value,
        })

    return rows
