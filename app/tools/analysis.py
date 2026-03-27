import pandas as pd
import re


def find_high_interest_low_conversion_products(df, min_views=1000, max_purchase_rate=0.005):
    filtered = df[
        (df["items_viewed"] >= min_views) &
        (df["view_to_purchase_rate"] <= max_purchase_rate)
    ].copy()

    filtered = filtered.sort_values(
        by=["items_viewed", "view_to_purchase_rate"],
        ascending=[False, True]
    )

    return filtered


def generate_simple_insights(df):
    insights = []

    for _, row in df.iterrows():
        item_name = row["item_name"]
        views = row["items_viewed"]
        carts = row["items_added_to_cart"]
        purchases = row["items_purchased"]
        cart_rate = row["view_to_cart_rate"]
        purchase_rate = row["view_to_purchase_rate"]

        if carts <= 5:
            reason = "interes pe produs, dar add to cart foarte slab"
            suggestion = "verifică pagina produsului, prețul, imaginile și claritatea ofertei"
        elif purchases == 0:
            reason = "oamenii intră și adaugă în coș, dar nu cumpără"
            suggestion = "investighează checkout-ul, costurile finale, livrarea și încrederea"
        else:
            reason = "produs cu volum mare, dar conversie finală slabă"
            suggestion = "merită analizat pe device, landing page, sursă de trafic și remarketing"

        insights.append({
            "item_name": item_name,
            "items_viewed": views,
            "items_added_to_cart": carts,
            "items_purchased": purchases,
            "view_to_cart_rate": cart_rate,
            "view_to_purchase_rate": purchase_rate,
            "diagnostic": reason,
            "next_step": suggestion,
        })

    return pd.DataFrame(insights)

def generate_device_insights(df):
    insights = []

    for _, row in df.iterrows():
        device = row["device"]
        sessions = row["sessions"]
        engagement_rate = row["engagement_rate"]
        purchases = row["purchases"]
        revenue_per_session = row["revenue_per_session"]

        if purchases == 0 and sessions > 500:
            diagnostic = "trafic există, dar fără cumpărări"
            action = "verifică experiența pe acest device și compară paginile cele mai vizitate"
        elif engagement_rate < 0.5:
            diagnostic = "engagement slab"
            action = "verifică viteza, layout-ul și claritatea ofertei pe acest device"
        else:
            diagnostic = "performanță acceptabilă"
            action = "merită comparat cu celelalte device-uri pentru optimizare"

        insights.append({
            "device": device,
            "sessions": sessions,
            "purchases": purchases,
            "engagement_rate": engagement_rate,
            "revenue_per_session": revenue_per_session,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)


def generate_landing_page_insights(df):
    insights = []

    for _, row in df.iterrows():
        landing_page = row["landing_page"]
        sessions = row["sessions"]
        engagement_rate = row["engagement_rate"]
        revenue_per_session = row["revenue_per_session"]

        if sessions > 1000 and revenue_per_session == 0:
            diagnostic = "trafic mare fără venit"
            action = "verifică relevanța traficului și calitatea paginii"
        elif engagement_rate < 0.5:
            diagnostic = "engagement slab pe pagină"
            action = "verifică mesajul principal, imaginile și viteza paginii"
        else:
            diagnostic = "pagină relativ sănătoasă"
            action = "compară cu paginile de top pentru idei de îmbunătățire"

        insights.append({
            "landing_page": landing_page,
            "sessions": sessions,
            "engagement_rate": engagement_rate,
            "revenue_per_session": revenue_per_session,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def generate_landing_page_conversion_insights(df):
    insights = []

    for _, row in df.iterrows():
        landing_page = row["landing_page"]
        sessions = row["sessions"]
        purchases = row["purchases"]
        engagement_rate = row["engagement_rate"]
        revenue_per_session = row["revenue_per_session"]

        if sessions > 1000 and purchases == 0:
            diagnostic = "trafic mare, fără cumpărări"
            action = "verifică relevanța traficului și calitatea paginii"
        elif engagement_rate < 0.5 and sessions > 500:
            diagnostic = "trafic există, dar engagement slab"
            action = "verifică mesajul principal, imaginile, viteza și UX-ul"
        elif revenue_per_session < 1 and sessions > 500:
            diagnostic = "venit slab raportat la trafic"
            action = "merită comparată cu paginile cele mai performante"
        else:
            diagnostic = "performanță relativ ok"
            action = "monitorizează și compară cu top pages"

        insights.append({
            "landing_page": landing_page,
            "sessions": sessions,
            "purchases": purchases,
            "engagement_rate": engagement_rate,
            "revenue_per_session": revenue_per_session,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def add_product_opportunity_score(df):
    scored = df.copy()

    scored["opportunity_score"] = (
        scored["items_viewed"] * (1 - scored["view_to_purchase_rate"])
    ).round(2)

    scored = scored.sort_values("opportunity_score", ascending=False)
    return scored


def add_landing_page_opportunity_score(df):
    scored = df.copy()

    scored["opportunity_score"] = (
        scored["sessions"] * (1 - scored["engagement_rate"]) * (1 / (scored["revenue_per_session"] + 1))
    ).round(2)

    scored = scored.sort_values("opportunity_score", ascending=False)
    return scored

def generate_traffic_campaign_insights(df):
    insights = []

    for _, row in df.iterrows():
        source_medium = row["source_medium"]
        campaign_name = row["campaign_name"]
        sessions = row["sessions"]
        purchases = row["purchases"]
        engagement_rate = row["engagement_rate"]
        revenue_per_session = row["revenue_per_session"]

        if sessions > 500 and purchases == 0:
            diagnostic = "trafic mare fără cumpărări"
            action = "verifică relevanța traficului și paginile de destinație"
        elif engagement_rate < 0.5 and sessions > 200:
            diagnostic = "engagement slab"
            action = "verifică intenția traficului, mesajul și landing page-ul"
        elif revenue_per_session < 1 and sessions > 200:
            diagnostic = "venit mic per sesiune"
            action = "compară această campanie cu cele mai bune surse/campanii"
        else:
            diagnostic = "performanță relativ ok"
            action = "monitorizează și compară cu top performers"

        insights.append({
            "source_medium": source_medium,
            "campaign_name": campaign_name,
            "sessions": sessions,
            "purchases": purchases,
            "engagement_rate": engagement_rate,
            "revenue_per_session": revenue_per_session,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def generate_campaign_product_insights(df):
    insights = []

    for _, row in df.iterrows():
        campaign_name = row["campaign_name"]
        item_name = row["item_name"]
        viewed = row["items_viewed"]
        carts = row["items_added_to_cart"]
        purchased = row["items_purchased"]
        purchase_rate = row["view_to_purchase_rate"]

        if viewed > 500 and purchased == 0:
            diagnostic = "produs cu interes în campanie, dar fără cumpărări"
            action = "verifică potrivirea dintre campanie, produs și pagina de destinație"
        elif carts > 10 and purchased == 0:
            diagnostic = "intră în coș, dar nu cumpără"
            action = "verifică prețul final, livrarea, ratele și checkout-ul"
        elif purchase_rate < 0.005 and viewed > 200:
            diagnostic = "conversie slabă în această campanie"
            action = "compară produsul cu altele din aceeași campanie"
        else:
            diagnostic = "performanță relativ ok"
            action = "monitorizează și compară cu top produse din campanie"

        insights.append({
            "campaign_name": campaign_name,
            "item_name": item_name,
            "items_viewed": viewed,
            "items_added_to_cart": carts,
            "items_purchased": purchased,
            "view_to_purchase_rate": purchase_rate,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def generate_product_channel_insights(df):
    insights = []

    for _, row in df.iterrows():
        item_name = row["item_name"]
        source_medium = row["source_medium"]
        campaign_name = row["campaign_name"]
        viewed = row["items_viewed"]
        carts = row["items_added_to_cart"]
        purchased = row["items_purchased"]
        purchase_rate = row["view_to_purchase_rate"]

        if viewed > 200 and purchased == 0:
            diagnostic = "produs văzut, dar fără cumpărări din această sursă"
            action = "verifică intenția traficului și potrivirea dintre mesaj și produs"
        elif carts > 10 and purchased == 0:
            diagnostic = "produs adăugat în coș, dar fără cumpărări"
            action = "verifică prețul final, livrarea și checkout-ul"
        elif purchase_rate < 0.005 and viewed > 100:
            diagnostic = "conversie slabă pe acest produs din această sursă"
            action = "compară cu alte surse sau campanii pentru același produs"
        else:
            diagnostic = "performanță relativ ok"
            action = "monitorizează și compară cu sursele mai bune"

        insights.append({
            "item_name": item_name,
            "source_medium": source_medium,
            "campaign_name": campaign_name,
            "items_viewed": viewed,
            "items_added_to_cart": carts,
            "items_purchased": purchased,
            "view_to_purchase_rate": purchase_rate,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def generate_campaign_audience_interest_insights(df):
    insights = []

    for _, row in df.iterrows():
        campaign_name = row["campaign_name"]
        audience_name = row["audience_name"]
        branding_interest = row["branding_interest"]
        sessions = row["sessions"]
        purchases = row["purchases"]
        revenue = row["purchase_revenue"]

        if sessions >= 100 and purchases == 0:
            diagnostic = "audiență cu trafic, dar fără cumpărări"
            action = "merită verificată relevanța audienței pentru campania respectivă"
        elif purchases > 0 and revenue > 0:
            diagnostic = "audiență care a generat conversii"
            action = "compar-o cu alte audiențe din aceeași campanie"
        else:
            diagnostic = "semnal slab sau insuficient"
            action = "monitorizează pe o perioadă mai lungă"

        insights.append({
            "campaign_name": campaign_name,
            "audience_name": audience_name,
            "branding_interest": branding_interest,
            "sessions": sessions,
            "purchases": purchases,
            "purchase_revenue": revenue,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def generate_google_ads_product_insights(df):
    insights = []

    for _, row in df.iterrows():
        campaign_name = row["campaign_name"]
        product_title = row["product_title"]
        clicks = row["clicks"]
        cost = row["cost"]
        conversions = row["conversions"]
        roas = row["roas"]
        cpa = row["cpa"]

        if clicks > 100 and conversions == 0:
            diagnostic = "multe clickuri, fără conversii"
            action = "verifică pagina produsului, relevanța traficului și termenii de căutare"
        elif cost > 200 and conversions == 0:
            diagnostic = "cost mare fără rezultate"
            action = "merită redusă expunerea sau investigat produsul"
        elif roas < 2 and conversions > 0:
            diagnostic = "convertește, dar ROAS-ul este slab"
            action = "verifică marja, prețul și calitatea traficului"
        else:
            diagnostic = "performanță relativ ok"
            action = "compară cu produsele cele mai bune din aceeași campanie"

        insights.append({
            "campaign_name": campaign_name,
            "product_title": product_title,
            "clicks": clicks,
            "cost": cost,
            "conversions": conversions,
            "cpa": cpa,
            "roas": roas,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

import re


def normalize_product_name(text):
    if not text:
        return ""

    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\-]", "", text)
    return text


def merge_ads_and_ga4_products(ads_df, ga4_df):
    ads = ads_df.copy()
    ga4 = ga4_df.copy()

    ads["normalized_product"] = ads["product_title"].apply(normalize_product_name)
    ga4["normalized_product"] = ga4["item_name"].apply(normalize_product_name)

    merged = ads.merge(
        ga4,
        on="normalized_product",
        how="outer",
        suffixes=("_ads", "_ga4")
    )

    return merged

def merge_ads_and_ga4_products_by_id(ads_df, ga4_df):
    ads = ads_df.copy()
    ga4 = ga4_df.copy()

    ads["join_item_id"] = ads["product_item_id"].astype(str).str.strip()
    ga4["join_item_id"] = ga4["item_id"].astype(str).str.strip()

    merged = ads.merge(
        ga4,
        on="join_item_id",
        how="outer",
        suffixes=("_ads", "_ga4")
    )

    return merged


def generate_joined_product_insights(df):
    insights = []

    for _, row in df.iterrows():
        product_ads = row.get("product_title", "")
        product_ga4 = row.get("item_name", "")
        product_name = product_ads if pd.notna(product_ads) and product_ads else product_ga4

        clicks = row.get("clicks", 0) if pd.notna(row.get("clicks", 0)) else 0
        cost = row.get("cost", 0) if pd.notna(row.get("cost", 0)) else 0
        conversions_ads = row.get("conversions", 0) if pd.notna(row.get("conversions", 0)) else 0

        items_viewed = row.get("items_viewed", 0) if pd.notna(row.get("items_viewed", 0)) else 0
        items_added_to_cart = row.get("items_added_to_cart", 0) if pd.notna(row.get("items_added_to_cart", 0)) else 0
        items_purchased = row.get("items_purchased", 0) if pd.notna(row.get("items_purchased", 0)) else 0

        if clicks > 100 and items_viewed == 0:
            diagnostic = "Ads trimite clickuri, dar produsul nu apare în GA4"
            action = "verifică tracking-ul, landing page-ul sau nepotrivirea de nume produs"
        elif items_viewed > 200 and items_added_to_cart == 0:
            diagnostic = "produs văzut, dar fără add to cart"
            action = "verifică pagina produsului, prețul și claritatea ofertei"
        elif items_added_to_cart > 10 and items_purchased == 0:
            diagnostic = "produs ajunge în coș, dar nu cumpără"
            action = "verifică checkout-ul, costurile finale și încrederea"
        elif cost > 200 and conversions_ads == 0:
            diagnostic = "cost mare în Ads, fără conversii"
            action = "merită investigat sau redusă expunerea"
        else:
            diagnostic = "performanță relativ ok"
            action = "compară cu produsele cele mai bune"

        insights.append({
            "product_name": product_name,
            "clicks": clicks,
            "cost": cost,
            "conversions_ads": conversions_ads,
            "items_viewed": items_viewed,
            "items_added_to_cart": items_added_to_cart,
            "items_purchased": items_purchased,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def merge_ads_and_ga4_products_by_id(ads_df, ga4_df):
    ads = ads_df.copy()
    ga4 = ga4_df.copy()

    ads["join_item_id"] = ads["product_item_id"].astype(str).str.strip()
    ga4["join_item_id"] = ga4["item_id"].astype(str).str.strip()

    merged = ads.merge(
        ga4,
        on="join_item_id",
        how="outer",
        suffixes=("_ads", "_ga4")
    )

    return merged

def build_main_product_report(ads_df, ga4_source_df):
    ads = ads_df.copy()
    ga4 = ga4_source_df.copy()

    def summarize_campaigns(series):
        values = [str(v).strip() for v in series if str(v).strip() and str(v).strip() != "nan"]
        unique = []
        for value in values:
            if value not in unique:
                unique.append(value)
        if not unique:
            return "-"
        if len(unique) == 1:
            return unique[0]
        return f"{unique[0]} +{len(unique) - 1}"

    if ads.empty:
        ads = pd.DataFrame(columns=[
            "product_item_id", "product_title", "campaign_name", "clicks", "cost",
            "conversions", "conversion_value"
        ])

    if ga4.empty:
        ga4 = pd.DataFrame(columns=[
            "item_id", "item_name", "source_medium",
            "items_viewed", "items_added_to_cart", "items_purchased", "item_revenue"
        ])

    ads["join_item_id"] = ads["product_item_id"].astype(str).str.strip()
    ga4["join_item_id"] = ga4["item_id"].astype(str).str.strip()

    ads_agg = ads.groupby("join_item_id", as_index=False).agg({
        "product_item_id": "first",
        "product_title": "first",
        "campaign_name": summarize_campaigns,
        "clicks": "sum",
        "cost": "sum",
        "conversions": "sum",
        "conversion_value": "sum",
    })

    ads_agg["ads_roas"] = ads_agg.apply(
        lambda x: round(x["conversion_value"] / x["cost"], 2) if x["cost"] else 0,
        axis=1
    )

    ga4_total = ga4.groupby("join_item_id", as_index=False).agg({
        "item_name": "first",
        "items_viewed": "sum",
        "items_added_to_cart": "sum",
        "items_purchased": "sum",
        "item_revenue": "sum",
    }).rename(columns={
        "items_viewed": "ga4_views_total",
        "items_added_to_cart": "ga4_atc_total",
        "items_purchased": "ga4_purchases_total",
        "item_revenue": "ga4_revenue_total",
    })

    ga4_google = ga4[
        ga4["source_medium"].str.contains("google / cpc", case=False, na=False)
    ].groupby("join_item_id", as_index=False).agg({
        "items_viewed": "sum",
        "items_added_to_cart": "sum",
        "items_purchased": "sum",
        "item_revenue": "sum",
    }).rename(columns={
        "items_viewed": "ga4_views_google_cpc",
        "items_added_to_cart": "ga4_atc_google_cpc",
        "items_purchased": "ga4_purchases_google_cpc",
        "item_revenue": "ga4_revenue_google_cpc",
    })

    merged = ads_agg.merge(ga4_total, on="join_item_id", how="outer")
    merged = merged.merge(ga4_google, on="join_item_id", how="left")

    for col in [
        "clicks", "cost", "conversions", "conversion_value", "ads_roas",
        "ga4_views_total", "ga4_atc_total", "ga4_purchases_total", "ga4_revenue_total",
        "ga4_views_google_cpc", "ga4_atc_google_cpc", "ga4_purchases_google_cpc", "ga4_revenue_google_cpc"
    ]:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)

    merged["product_name"] = merged["product_title"].fillna(merged["item_name"])
    merged["item_id"] = merged["product_item_id"].fillna(merged["join_item_id"])
    if "campaign_name" not in merged.columns:
        merged["campaign_name"] = "-"

    merged["google_view_to_cart_rate"] = merged.apply(
    lambda x: round((x["ga4_atc_google_cpc"] / x["ga4_views_google_cpc"]) * 100, 2) if x["ga4_views_google_cpc"] else 0,
    axis=1
)

    merged["google_view_to_purchase_rate"] = merged.apply(
    lambda x: round((x["ga4_purchases_google_cpc"] / x["ga4_views_google_cpc"]) * 100, 2) if x["ga4_views_google_cpc"] else 0,
    axis=1
)

    return merged.sort_values(by="clicks", ascending=False)


def generate_main_product_report_insights(df):
    insights = []

    for _, row in df.iterrows():
        product_name = row.get("product_name", "")
        clicks = row.get("clicks", 0) or 0
        cost = row.get("cost", 0) or 0
        ads_roas = row.get("ads_roas", 0) or 0
        views_google = row.get("ga4_views_google_cpc", 0) or 0
        atc_google = row.get("ga4_atc_google_cpc", 0) or 0
        purchases_google = row.get("ga4_purchases_google_cpc", 0) or 0
        conversions_ads = row.get("conversions", 0) or 0
        status = row.get("status", "🟡 Monitorizare")

        if clicks > 100 and views_google == 0:
            diagnostic = "Ads trimite clickuri, dar produsul nu apare în GA4 pe google/cpc"
            action = "verifică tagging-ul, landing page-ul și tracking-ul"
        elif views_google > 300 and atc_google == 0:
            diagnostic = "produs văzut din Google Ads, dar fără add to cart"
            action = "verifică pagina produsului, imaginile, oferta și prețul"
        elif atc_google >= 15 and purchases_google == 0:
            diagnostic = "produsul intră în coș, dar nu cumpără"
            action = "verifică checkout-ul, costurile finale, livrarea și încrederea"
        elif cost >= 300 and conversions_ads == 0:
            diagnostic = "cost mare în Ads fără conversii"
            action = "redu expunerea sau investighează potrivirea dintre produs și campanie"
        elif ads_roas < 2 and cost >= 200:
            diagnostic = "produsul convertește slab raportat la cost"
            action = "verifică marja, termenii de căutare și intenția traficului"
        elif status == "🟢 Bun":
            diagnostic = "produs cu performanță bună"
            action = "compară-l cu alte produse și folosește-l ca benchmark"
        else:
            diagnostic = "produsul trebuie monitorizat"
            action = "urmărește evoluția pe perioade și compară-l cu media"

        insights.append({
            "product_name": product_name,
            "status": status,
            "clicks": clicks,
            "cost": cost,
            "ads_roas": ads_roas,
            "ga4_views_google_cpc": views_google,
            "ga4_atc_google_cpc": atc_google,
            "ga4_purchases_google_cpc": purchases_google,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def add_product_status(df):
    result = df.copy()

    def compute_status(row):
        cost = row.get("cost", 0) or 0
        clicks = row.get("clicks", 0) or 0
        roas = row.get("ads_roas", 0) or 0
        views_google = row.get("ga4_views_google_cpc", 0) or 0
        atc_google = row.get("ga4_atc_google_cpc", 0) or 0
        purchases_google = row.get("ga4_purchases_google_cpc", 0) or 0
        conversions_ads = row.get("conversions", 0) or 0

        if cost >= 300 and conversions_ads == 0:
            return "🔴 Problematic"

        if views_google >= 300 and atc_google == 0:
            return "🔴 Problematic"

        if atc_google >= 15 and purchases_google == 0:
            return "🔴 Problematic"

        if cost >= 200 and roas < 2:
            return "🟠 Atenție"

        if clicks >= 100 and purchases_google > 0 and roas >= 4:
            return "🟢 Bun"

        if purchases_google >= 3 and roas >= 3:
            return "🟢 Bun"

        return "🟡 Monitorizare"

    result["status"] = result.apply(compute_status, axis=1)
    return result

def clean_meta_product_id(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if "," in value:
        return value.split(",")[0].strip()

    return value


def extract_meta_product_name(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if "," in value:
        parts = value.split(",", 1)
        if len(parts) == 2:
            return parts[1].strip()

    return value


def build_omnichannel_product_report(google_df, meta_df, ga4_df):
    google = google_df.copy()
    meta = meta_df.copy()
    ga4 = ga4_df.copy()

    if google.empty:
        google = pd.DataFrame(columns=[
            "product_item_id", "product_title", "clicks", "cost",
            "conversions", "conversion_value"
        ])

    if meta.empty:
        meta = pd.DataFrame(columns=[
            "product_id", "campaign_name", "clicks", "spend",
            "view_content", "add_to_cart"
        ])

    if ga4.empty:
        ga4 = pd.DataFrame(columns=[
            "item_id", "item_name", "source_medium",
            "items_viewed", "items_added_to_cart", "items_purchased", "item_revenue"
        ])

    google["join_item_id"] = google["product_item_id"].astype(str).str.strip()
    meta["join_item_id"] = meta["product_id"].apply(clean_meta_product_id).astype(str).str.strip()
    meta["meta_product_name"] = meta["product_id"].apply(extract_meta_product_name)
    ga4["join_item_id"] = ga4["item_id"].astype(str).str.strip()

    google_agg = google.groupby("join_item_id", as_index=False).agg({
        "product_title": "first",
        "clicks": "sum",
        "cost": "sum",
        "conversions": "sum",
        "conversion_value": "sum",
    }).rename(columns={
        "clicks": "google_clicks",
        "cost": "google_cost",
        "conversions": "google_conversions",
        "conversion_value": "google_conversion_value",
    })

    google_agg["google_roas"] = google_agg.apply(
        lambda x: round(x["google_conversion_value"] / x["google_cost"], 2) if x["google_cost"] else 0,
        axis=1
    )

    meta_agg = meta.groupby("join_item_id", as_index=False).agg({
    "meta_product_name": "first",
    "clicks": "sum",
    "spend": "sum",
    "view_content": "sum",
    "add_to_cart": "sum",
}).rename(columns={
    "clicks": "meta_clicks",
    "spend": "meta_cost",
    "view_content": "meta_view_content",
    "add_to_cart": "meta_add_to_cart",
})

    ga4_total = ga4.groupby("join_item_id", as_index=False).agg({
        "item_name": "first",
        "items_viewed": "sum",
        "items_added_to_cart": "sum",
        "items_purchased": "sum",
        "item_revenue": "sum",
    }).rename(columns={
        "items_viewed": "ga4_views_total",
        "items_added_to_cart": "ga4_atc_total",
        "items_purchased": "ga4_purchases_total",
        "item_revenue": "ga4_revenue_total",
    })

    ga4_google = ga4[
        ga4["source_medium"].str.contains("google / cpc", case=False, na=False)
    ].groupby("join_item_id", as_index=False).agg({
        "items_viewed": "sum",
        "items_added_to_cart": "sum",
        "items_purchased": "sum",
    }).rename(columns={
        "items_viewed": "ga4_views_google_cpc",
        "items_added_to_cart": "ga4_atc_google_cpc",
        "items_purchased": "ga4_purchases_google_cpc",
    })

    ga4_meta = ga4[
        ga4["source_medium"].str.contains("facebook|instagram|meta", case=False, na=False)
    ].groupby("join_item_id", as_index=False).agg({
        "items_viewed": "sum",
        "items_added_to_cart": "sum",
        "items_purchased": "sum",
    }).rename(columns={
        "items_viewed": "ga4_views_meta",
        "items_added_to_cart": "ga4_atc_meta",
        "items_purchased": "ga4_purchases_meta",
    })

    merged = google_agg.merge(meta_agg, on="join_item_id", how="outer")
    merged = merged.merge(ga4_total, on="join_item_id", how="outer")
    merged = merged.merge(ga4_google, on="join_item_id", how="left")
    merged = merged.merge(ga4_meta, on="join_item_id", how="left")

    numeric_cols = [
        "google_clicks", "google_cost", "google_conversions", "google_conversion_value", "google_roas",
        "meta_clicks", "meta_cost", "meta_view_content", "meta_add_to_cart",
        "ga4_views_total", "ga4_atc_total", "ga4_purchases_total", "ga4_revenue_total",
        "ga4_views_google_cpc", "ga4_atc_google_cpc", "ga4_purchases_google_cpc",
        "ga4_views_meta", "ga4_atc_meta", "ga4_purchases_meta",
    ]

    for col in numeric_cols:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)

    merged["product_name"] = (
    merged["product_title"]
    .fillna(merged.get("item_name"))
    .fillna(merged.get("meta_product_name"))
)

    merged["google_view_to_purchase_rate"] = merged.apply(
        lambda x: round((x["ga4_purchases_google_cpc"] / x["ga4_views_google_cpc"]) * 100, 2) if x["ga4_views_google_cpc"] else 0,
        axis=1
    )

    merged["meta_view_to_purchase_rate"] = merged.apply(
        lambda x: round((x["ga4_purchases_meta"] / x["ga4_views_meta"]) * 100, 2) if x["ga4_views_meta"] else 0,
        axis=1
    )

    return merged.sort_values(by=["google_cost", "meta_cost"], ascending=[False, False])


def generate_omnichannel_product_insights(df):
    insights = []

    for _, row in df.iterrows():
        product_name = row.get("product_name", "")
        google_cost = row.get("google_cost", 0) or 0
        google_roas = row.get("google_roas", 0) or 0
        meta_cost = row.get("meta_cost", 0) or 0
        meta_atc = row.get("meta_add_to_cart", 0) or 0
        ga4_google_purchases = row.get("ga4_purchases_google_cpc", 0) or 0
        ga4_meta_purchases = row.get("ga4_purchases_meta", 0) or 0
        winner_channel = row.get("winner_channel", "Mixed")
        omnichannel_status = row.get("omnichannel_status", "🟡 Monitorizare")
        score = row.get("omnichannel_opportunity_score", 0)

        if google_cost > 200 and google_roas < 2:
            diagnostic = "Google Ads slab pe acest produs"
            action = "verifică termenii, pagina și marja"
        elif meta_cost > 100 and meta_atc == 0:
            diagnostic = "Meta consumă buget fără semnale de progres"
            action = "verifică creativul, audiența și landing page-ul"
        elif ga4_google_purchases > ga4_meta_purchases:
            diagnostic = "produsul performează mai bine din Google"
            action = "poți prioritiza search și trafic cu intenție mare"
        elif ga4_meta_purchases > ga4_google_purchases:
            diagnostic = "produsul performează mai bine din Meta"
            action = "testează mai mult creativul și prospectarea"
        else:
            diagnostic = "performanță mixtă omni-channel"
            action = "compară canalele și optimizează după cost și purchases"

        insights.append({
            "product_name": product_name,
            "winner_channel": winner_channel,
            "omnichannel_status": omnichannel_status,
            "opportunity_score": score,
            "google_cost": google_cost,
            "google_roas": google_roas,
            "meta_cost": meta_cost,
            "meta_add_to_cart": meta_atc,
            "ga4_purchases_google_cpc": ga4_google_purchases,
            "ga4_purchases_meta": ga4_meta_purchases,
            "diagnostic": diagnostic,
            "next_step": action,
        })

    return pd.DataFrame(insights)

def add_omnichannel_labels(df):
    result = df.copy()

    def get_winner_channel(row):
        google_purchases = row.get("ga4_purchases_google_cpc", 0) or 0
        meta_purchases = row.get("ga4_purchases_meta", 0) or 0
        google_roas = row.get("google_roas", 0) or 0
        meta_atc = row.get("meta_add_to_cart", 0) or 0

        if google_purchases > meta_purchases and google_roas >= 3:
            return "Google"
        if meta_purchases > google_purchases and meta_atc > 0:
            return "Meta"
        if google_purchases == 0 and meta_purchases == 0:
            return "Niciunul"
        return "Mixed"

    def get_omnichannel_status(row):
        google_cost = row.get("google_cost", 0) or 0
        google_roas = row.get("google_roas", 0) or 0
        meta_cost = row.get("meta_cost", 0) or 0
        meta_atc = row.get("meta_add_to_cart", 0) or 0
        google_purchases = row.get("ga4_purchases_google_cpc", 0) or 0
        meta_purchases = row.get("ga4_purchases_meta", 0) or 0

        if google_cost >= 300 and google_roas < 2 and meta_cost >= 100 and meta_atc == 0:
            return "🔴 Problematic"
        if google_cost >= 200 and google_roas < 2:
            return "🟠 Atenție"
        if meta_cost >= 100 and meta_atc == 0:
            return "🟠 Atenție"
        if google_purchases > 0 or meta_purchases > 0:
            if google_roas >= 3 or meta_atc > 0:
                return "🟢 Bun"
        return "🟡 Monitorizare"

    def get_opportunity_score(row):
        google_cost = row.get("google_cost", 0) or 0
        meta_cost = row.get("meta_cost", 0) or 0
        total_views = row.get("ga4_views_total", 0) or 0
        total_purchases = row.get("ga4_purchases_total", 0) or 0

        purchase_penalty = 1
        if total_views > 0:
            purchase_penalty = 1 - (total_purchases / total_views)

        score = (google_cost + meta_cost) * purchase_penalty
        return round(score, 2)

    result["winner_channel"] = result.apply(get_winner_channel, axis=1)
    result["omnichannel_status"] = result.apply(get_omnichannel_status, axis=1)
    result["omnichannel_opportunity_score"] = result.apply(get_opportunity_score, axis=1)

    return result

def build_pmax_feed_vs_other_report(campaign_df, product_df):
    campaigns = campaign_df.copy()
    products = product_df.copy()

    if campaigns.empty:
        campaigns = pd.DataFrame(columns=[
            "campaign_id", "campaign_name", "clicks", "cost",
            "conversions", "conversion_value"
        ])

    if products.empty:
        products = pd.DataFrame(columns=[
            "campaign_id", "campaign_name", "clicks", "cost",
            "conversions", "conversion_value"
        ])

    campaign_agg = campaigns.groupby(
        ["campaign_id", "campaign_name"], as_index=False
    ).agg({
        "clicks": "sum",
        "cost": "sum",
        "conversions": "sum",
        "conversion_value": "sum",
    }).rename(columns={
        "clicks": "total_clicks",
        "cost": "total_cost",
        "conversions": "total_conversions",
        "conversion_value": "total_conversion_value",
    })

    product_agg = products.groupby(
        ["campaign_id", "campaign_name"], as_index=False
    ).agg({
        "clicks": "sum",
        "cost": "sum",
    }).rename(columns={
        "clicks": "product_clicks_estimate",
        "cost": "product_cost_estimate",
    })

    merged = campaign_agg.merge(
        product_agg,
        on=["campaign_id", "campaign_name"],
        how="left"
    )

    merged["product_clicks_estimate"] = merged["product_clicks_estimate"].fillna(0)
    merged["product_cost_estimate"] = merged["product_cost_estimate"].fillna(0)

    merged["other_clicks_estimate"] = (
        merged["total_clicks"] - merged["product_clicks_estimate"]
    ).clip(lower=0)

    merged["other_cost_estimate"] = (
        merged["total_cost"] - merged["product_cost_estimate"]
    ).clip(lower=0)

    merged["feed_share_pct"] = merged.apply(
        lambda x: round((x["product_clicks_estimate"] / x["total_clicks"]) * 100, 2)
        if x["total_clicks"] else 0,
        axis=1
    )

    def label_row(row):
        pct = row["feed_share_pct"]
        if pct >= 70:
            return "🟢 Feed-heavy"
        if pct >= 30:
            return "🟡 Mixed"
        return "🟠 Other-heavy"

    merged["traffic_profile"] = merged.apply(label_row, axis=1)

    return merged.sort_values("total_cost", ascending=False)


def add_totals_row(df):
    if df.empty:
        return df

    totals = {
        "campaign_id": "",
        "campaign_name": "TOTAL",
        "total_clicks": df["total_clicks"].sum(),
        "product_clicks_estimate": df["product_clicks_estimate"].sum(),
        "other_clicks_estimate": df["other_clicks_estimate"].sum(),
        "feed_share_pct": round(
            (df["product_clicks_estimate"].sum() / df["total_clicks"].sum()) * 100, 2
        ) if df["total_clicks"].sum() else 0,
        "total_cost": round(df["total_cost"].sum(), 2),
        "product_cost_estimate": round(df["product_cost_estimate"].sum(), 2),
        "other_cost_estimate": round(df["other_cost_estimate"].sum(), 2),
        "total_conversions": round(df["total_conversions"].sum(), 2),
        "total_conversion_value": round(df["total_conversion_value"].sum(), 2),
        "traffic_profile": "",
    }

    return pd.concat([df, pd.DataFrame([totals])], ignore_index=True)

def get_previous_ga4_range(start_date, end_date):
    mapping = {
        ("7daysAgo", "today"): ("14daysAgo", "8daysAgo"),
        ("30daysAgo", "today"): ("60daysAgo", "31daysAgo"),
    }
    return mapping.get((start_date, end_date), ("60daysAgo", "31daysAgo"))

