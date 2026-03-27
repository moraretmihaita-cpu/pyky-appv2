from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest, FilterExpression, Filter

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from app.config import GA4_PROPERTY_ID

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def get_credentials():
    creds = None

    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    except Exception:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("oauth_client.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

def get_landing_pages_report(start_date="30daysAgo", end_date="today", limit=200):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="landingPage"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="totalRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    response = client.run_report(request)
    return response

def get_product_funnel_report(start_date="30daysAgo", end_date="today", limit=1000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="itemName")],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemsPurchased"),
            Metric(name="itemRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_product_funnel_report_with_id(start_date="30daysAgo", end_date="today", limit=1000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="itemId"),
            Dimension(name="itemName"),
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemsPurchased"),
            Metric(name="itemRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_device_report(start_date="30daysAgo", end_date="today", limit=20):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="deviceCategory")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="purchaseRevenue"),
            Metric(name="ecommercePurchases"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_landing_page_conversion_report(start_date="30daysAgo", end_date="today", limit=1000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="landingPage")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_traffic_campaign_report(start_date="30daysAgo", end_date="today", limit=1000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionSourceMedium"),
            Dimension(name="sessionCampaignName"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_campaign_product_report(start_date="30daysAgo", end_date="today", limit=1000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionCampaignName"),
            Dimension(name="itemName"),
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemsPurchased"),
            Metric(name="itemRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_product_source_campaign_report(start_date="30daysAgo", end_date="today", limit=1000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="itemName"),
            Dimension(name="sessionSourceMedium"),
            Dimension(name="sessionCampaignName"),
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemsPurchased"),
            Metric(name="itemRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_campaign_audience_interest_report(start_date="30daysAgo", end_date="today", limit=1000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionCampaignName"),
            Dimension(name="audienceName"),
            Dimension(name="brandingInterest"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_product_source_report_with_id(start_date="30daysAgo", end_date="today", limit=1500):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="itemId"),
            Dimension(name="itemName"),
            Dimension(name="sessionSourceMedium"),
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemsPurchased"),
            Metric(name="itemRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_product_source_medium_performance_report(start_date="30daysAgo", end_date="today", limit=1000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="itemId"),
            Dimension(name="itemName"),
            Dimension(name="sessionSourceMedium"),
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemsPurchased"),
            Metric(name="itemRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

def get_all_products_list(start_date="30daysAgo", end_date="today", limit=3000):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="itemId"),
            Dimension(name="itemName"),
        ],
        metrics=[
            Metric(name="itemsViewed"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)

FAVI_SOURCE_MEDIUM = "favi.ro / cpc"


def _source_medium_exact_filter(source_medium=FAVI_SOURCE_MEDIUM):
    return FilterExpression(
        filter=Filter(
            field_name="sessionSourceMedium",
            string_filter=Filter.StringFilter(
                match_type=Filter.StringFilter.MatchType.EXACT,
                value=source_medium,
            ),
        )
    )


def get_favi_overview_report(start_date="30daysAgo", end_date="today", source_medium=FAVI_SOURCE_MEDIUM):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
        ],
        dimension_filter=_source_medium_exact_filter(source_medium),
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=10,
    )

    return client.run_report(request)


def get_favi_product_report(start_date="30daysAgo", end_date="today", source_medium=FAVI_SOURCE_MEDIUM, limit=1500):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="itemId"),
            Dimension(name="itemName"),
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemsPurchased"),
            Metric(name="itemRevenue"),
        ],
        dimension_filter=_source_medium_exact_filter(source_medium),
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)


def get_favi_landing_pages_report(start_date="30daysAgo", end_date="today", source_medium=FAVI_SOURCE_MEDIUM, limit=1500):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="landingPage")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
        ],
        dimension_filter=_source_medium_exact_filter(source_medium),
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)


def get_favi_device_report(start_date="30daysAgo", end_date="today", source_medium=FAVI_SOURCE_MEDIUM, limit=20):
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="deviceCategory")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
        ],
        dimension_filter=_source_medium_exact_filter(source_medium),
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    return client.run_report(request)
