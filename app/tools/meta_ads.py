import requests
from app.config import (
    META_ACCESS_TOKEN,
    META_AD_ACCOUNT_ID,
)

BASE_URL = "https://graph.facebook.com/v23.0"


def get_meta_campaign_performance(date_preset="last_30d"):
    url = f"{BASE_URL}/{META_AD_ACCOUNT_ID}/insights"

    params = {
        "access_token": META_ACCESS_TOKEN,
        "level": "campaign",
        "fields": ",".join([
            "campaign_name",
            "impressions",
            "clicks",
            "spend",
            "actions",
            "action_values",
        ]),
        "date_preset": date_preset,
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json().get("data", [])

    rows = []
    for row in data:
        purchases = 0
        purchase_value = 0

        for action in row.get("actions", []):
            if action.get("action_type") == "purchase":
                purchases = float(action.get("value", 0))

        for action_value in row.get("action_values", []):
            if action_value.get("action_type") == "purchase":
                purchase_value = float(action_value.get("value", 0))

        rows.append({
            "campaign_name": row.get("campaign_name"),
            "impressions": int(row.get("impressions", 0)),
            "clicks": int(row.get("clicks", 0)),
            "spend": float(row.get("spend", 0)),
            "purchases": purchases,
            "purchase_value": purchase_value,
        })

    return rows


def get_meta_adset_performance(date_preset="last_30d"):
    url = f"{BASE_URL}/{META_AD_ACCOUNT_ID}/insights"

    params = {
        "access_token": META_ACCESS_TOKEN,
        "level": "adset",
        "fields": ",".join([
            "campaign_name",
            "adset_name",
            "impressions",
            "clicks",
            "spend",
            "actions",
            "action_values",
        ]),
        "date_preset": date_preset,
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json().get("data", [])

    rows = []
    for row in data:
        purchases = 0
        purchase_value = 0

        for action in row.get("actions", []):
            if action.get("action_type") == "purchase":
                purchases = float(action.get("value", 0))

        for action_value in row.get("action_values", []):
            if action_value.get("action_type") == "purchase":
                purchase_value = float(action_value.get("value", 0))

        rows.append({
            "campaign_name": row.get("campaign_name"),
            "adset_name": row.get("adset_name"),
            "impressions": int(row.get("impressions", 0)),
            "clicks": int(row.get("clicks", 0)),
            "spend": float(row.get("spend", 0)),
            "purchases": purchases,
            "purchase_value": purchase_value,
        })

    return rows

def get_meta_product_performance(date_preset="last_30d"):
    url = f"{BASE_URL}/{META_AD_ACCOUNT_ID}/insights"

    params = {
        "access_token": META_ACCESS_TOKEN,
        "level": "campaign",
        "fields": ",".join([
            "campaign_name",
            "impressions",
            "clicks",
            "spend",
            "actions",
        ]),
        "breakdowns": "product_id",
        "date_preset": date_preset,
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json().get("data", [])

    rows = []
    for row in data:
        view_content = 0
        add_to_cart = 0

        for action in row.get("actions", []):
            action_type = action.get("action_type", "")
            value = float(action.get("value", 0))

            if "view_content" in action_type:
                view_content += value

            if "add_to_cart" in action_type:
                add_to_cart += value

        rows.append({
            "campaign_name": row.get("campaign_name"),
            "product_id": row.get("product_id"),
            "impressions": int(row.get("impressions", 0)),
            "clicks": int(row.get("clicks", 0)),
            "spend": float(row.get("spend", 0)),
            "view_content": view_content,
            "add_to_cart": add_to_cart,
        })

    return rows