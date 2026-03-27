import pandas as pd
from app.tools.ga4 import get_product_funnel_report
from app.tools.analysis import (
    find_high_interest_low_conversion_products,
    generate_simple_insights,
)
from app.tools.ads import get_campaign_performance

rows = get_campaign_performance()

for row in rows:
    print(row)

from app.tools.ads import get_product_performance

rows = get_product_performance()

for row in rows[:10]:
    print(row)

from app.tools.meta_ads import get_meta_campaign_performance

rows = get_meta_campaign_performance()

for row in rows:
    print(row)

response = get_product_funnel_report()

rows = []
for row in response.rows:
    rows.append({
        "item_name": row.dimension_values[0].value,
        "items_viewed": int(row.metric_values[0].value),
        "items_added_to_cart": int(row.metric_values[1].value),
        "items_purchased": int(row.metric_values[2].value),
        "item_revenue": float(row.metric_values[3].value),
    })

df = pd.DataFrame(rows)
df["view_to_cart_rate"] = (df["items_added_to_cart"] / df["items_viewed"]).round(4)
df["view_to_purchase_rate"] = (df["items_purchased"] / df["items_viewed"]).round(4)

result = find_high_interest_low_conversion_products(df)
insights = generate_simple_insights(result)

print(insights.to_string(index=False))

from app.tools.ga4 import get_landing_pages_report

response = get_landing_pages_report()

for row in response.rows:
    print(
        row.dimension_values[0].value,
        row.metric_values[0].value,
        row.metric_values[1].value,
        row.metric_values[2].value,
    )

    from app.tools.ga4 import get_product_funnel_report

response = get_product_funnel_report()

for row in response.rows:
    print(
        row.dimension_values[0].value,
        row.metric_values[0].value,
        row.metric_values[1].value,
        row.metric_values[2].value,
        row.metric_values[3].value,
    )