"""
01_data_cleaning.py
Supply Chain & Delivery Operations Analytics — Olist Brazilian E-commerce
---------------------------------------------------------------------------
Loads all 9 raw Olist tables, joins them into a unified order-level dataset,
derives delivery KPIs, and exports analysis-ready CSVs.

Inputs : data/olist_*.csv + product_category_name_translation.csv
Outputs: data/cleaned_orders.csv
         data/seller_summary.csv
"""

import pandas as pd
import numpy as np
import os

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'input')

# ── 1. Load all tables ────────────────────────────────────────────────────────
print("Loading raw tables...")
orders    = pd.read_csv(f'{INPUT_DIR}/olist_orders_dataset.csv')
items     = pd.read_csv(f'{INPUT_DIR}/olist_order_items_dataset.csv')
customers = pd.read_csv(f'{INPUT_DIR}/olist_customers_dataset.csv')
sellers   = pd.read_csv(f'{INPUT_DIR}/olist_sellers_dataset.csv')
products  = pd.read_csv(f'{INPUT_DIR}/olist_products_dataset.csv')
reviews   = pd.read_csv(f'{INPUT_DIR}/olist_order_reviews_dataset.csv')
payments  = pd.read_csv(f'{INPUT_DIR}/olist_order_payments_dataset.csv')
category  = pd.read_csv(f'{INPUT_DIR}/product_category_name_translation.csv')

print(f"  Orders    : {len(orders):,}")
print(f"  Items     : {len(items):,}")
print(f"  Customers : {len(customers):,}")
print(f"  Products  : {len(products):,}")
print(f"  Sellers   : {len(sellers):,}")
print(f"  Reviews   : {len(reviews):,}")
print(f"  Payments  : {len(payments):,}")

# ── 2. Parse timestamps ───────────────────────────────────────────────────────
date_cols = [
    'order_purchase_timestamp', 'order_approved_at',
    'order_delivered_carrier_date', 'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors='coerce')

# ── 3. Filter delivered orders only ──────────────────────────────────────────
delivered = orders[orders['order_status'] == 'delivered'].copy()
print(f"\n  Delivered orders : {len(delivered):,} of {len(orders):,} total")

# Drop rows with missing critical delivery timestamps
delivered = delivered.dropna(subset=[
    'order_delivered_customer_date',
    'order_estimated_delivery_date',
    'order_purchase_timestamp'
])
print(f"  After null drop  : {len(delivered):,}")

# ── 4. Derive delivery KPIs ───────────────────────────────────────────────────
delivered['delivery_days_actual'] = (
    delivered['order_delivered_customer_date'] -
    delivered['order_purchase_timestamp']
).dt.days

delivered['delivery_days_estimated'] = (
    delivered['order_estimated_delivery_date'] -
    delivered['order_purchase_timestamp']
).dt.days

delivered['delay_days'] = (
    delivered['order_delivered_customer_date'] -
    delivered['order_estimated_delivery_date']
).dt.days

delivered['is_late']    = (delivered['delay_days'] > 0).astype(int)
delivered['is_on_time'] = (delivered['delay_days'] <= 0).astype(int)

delivered['YearMonth'] = delivered['order_purchase_timestamp'].dt.to_period('M').astype(str)
delivered['Year']      = delivered['order_purchase_timestamp'].dt.year
delivered['Month']     = delivered['order_purchase_timestamp'].dt.month
delivered['DayOfWeek'] = delivered['order_purchase_timestamp'].dt.day_name()

# ── 5. Aggregate items per order ──────────────────────────────────────────────
items_agg = items.groupby('order_id').agg(
    order_value    = ('price',         'sum'),
    freight_value  = ('freight_value', 'sum'),
    item_count     = ('order_item_id', 'count'),
    seller_id      = ('seller_id',     'first'),
    product_id     = ('product_id',    'first')
).reset_index()

# ── 6. Aggregate payments per order ──────────────────────────────────────────
pay_agg = payments.groupby('order_id').agg(
    payment_value  = ('payment_value',        'sum'),
    payment_type   = ('payment_type',         'first'),
    installments   = ('payment_installments', 'max')
).reset_index()

# ── 7. Best review per order ──────────────────────────────────────────────────
rev_agg = reviews.groupby('order_id').agg(
    review_score = ('review_score', 'mean')
).reset_index()

# ── 8. Translate product categories ──────────────────────────────────────────
category.columns = category.columns.str.strip().str.replace('\ufeff', '')
products = products.merge(category, on='product_category_name', how='left')

# ── 9. Master join ────────────────────────────────────────────────────────────
df = delivered \
    .merge(items_agg,                      on='order_id',    how='left') \
    .merge(pay_agg,                        on='order_id',    how='left') \
    .merge(rev_agg,                        on='order_id',    how='left') \
    .merge(customers[['customer_id',
                       'customer_state',
                       'customer_city']],  on='customer_id', how='left') \
    .merge(sellers[['seller_id',
                    'seller_state',
                    'seller_city']],       on='seller_id',   how='left') \
    .merge(products[['product_id',
                     'product_category_name_english',
                     'product_weight_g']],  on='product_id',  how='left')

# ── 10. Derived ratio ─────────────────────────────────────────────────────────
df['freight_ratio'] = (df['freight_value'] / df['order_value'].replace(0, np.nan)).round(4)

# ── 11. Drop outliers ─────────────────────────────────────────────────────────
df = df[(df['delivery_days_actual'] > 0) & (df['delivery_days_actual'] < 180)]
df = df[(df['order_value'] > 0)]

# ── 12. Export cleaned orders ─────────────────────────────────────────────────
df.to_csv(f'{DATA_DIR}/cleaned_orders.csv', index=False)

# ── 13. Seller summary ────────────────────────────────────────────────────────
seller_summary = df.groupby('seller_id').agg(
    seller_state        = ('seller_state',         'first'),
    total_orders        = ('order_id',             'count'),
    total_revenue       = ('order_value',          'sum'),
    avg_review_score    = ('review_score',         'mean'),
    late_orders         = ('is_late',              'sum'),
    avg_delay_days      = ('delay_days',           'mean'),
    avg_delivery_days   = ('delivery_days_actual', 'mean'),
    total_freight       = ('freight_value',        'sum')
).reset_index()

seller_summary['late_rate_pct'] = (
    seller_summary['late_orders'] / seller_summary['total_orders'] * 100
).round(1)

seller_summary['avg_review_score'] = seller_summary['avg_review_score'].round(2)
seller_summary['avg_delay_days']   = seller_summary['avg_delay_days'].round(1)
seller_summary['avg_delivery_days']= seller_summary['avg_delivery_days'].round(1)
seller_summary['total_revenue']    = seller_summary['total_revenue'].round(2)

seller_summary.to_csv(f'{DATA_DIR}/seller_summary.csv', index=False)

# ── 14. Summary ───────────────────────────────────────────────────────────────
print(f"\n  Clean orders     : {len(df):,}")
print(f"  Unique customers : {df['customer_id'].nunique():,}")
print(f"  Unique sellers   : {df['seller_id'].nunique():,}")
print(f"  Unique products  : {df['product_id'].nunique():,}")
print(f"  Date range       : {df['order_purchase_timestamp'].min().date()} to {df['order_purchase_timestamp'].max().date()}")
print(f"  Total revenue    : R${df['order_value'].sum():,.0f}")
print(f"  On-time rate     : {df['is_on_time'].mean()*100:.1f}%")
print(f"  Avg delay (late) : {df[df['is_late']==1]['delay_days'].mean():.1f} days")
print(f"  Avg review score : {df['review_score'].mean():.2f} / 5.0")
print(f"  States covered   : {df['customer_state'].nunique()}")
print(f"\n[01] Cleaning complete. Output -> data/cleaned_orders.csv + data/seller_summary.csv")
