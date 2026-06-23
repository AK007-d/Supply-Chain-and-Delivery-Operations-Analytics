"""
04_load_mysql.py
Supply Chain & Delivery Operations Analytics — Olist Brazilian E-commerce
---------------------------------------------------------------------------
Batch-loads cleaned CSVs into MySQL.
Run AFTER 00_mysql_setup.sql has been executed.

Prerequisites:
    pip install mysql-connector-python pandas

Usage:
    python scripts/04_load_mysql.py \
        --host localhost --user root --password yourpassword
"""

import pandas as pd
import argparse
import os
import sys

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'input')

def load(host, user, password, database='olist_analytics', port=3306):
    try:
        import mysql.connector
    except ImportError:
        print("Install: pip install mysql-connector-python")
        sys.exit(1)

    print(f"Connecting to MySQL at {host}:{port} ...")
    conn = mysql.connector.connect(
        host=host, user=user, password=password,
        database=database, port=port
    )
    cursor = conn.cursor()
    print("  Connected.\n")

    # ── Load cleaned_orders ───────────────────────────────────
    print("Loading cleaned_orders ...")
    df = pd.read_csv(f'{DATA_DIR}/cleaned_orders.csv')
    df['order_purchase_timestamp']      = pd.to_datetime(df['order_purchase_timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['order_approved_at']             = pd.to_datetime(df['order_approved_at'],            errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    df['order_delivered_carrier_date']  = pd.to_datetime(df['order_delivered_carrier_date'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'],errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'],errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.where(pd.notnull(df), None)

    cursor.execute("TRUNCATE TABLE cleaned_orders")
    cols = ['order_id','customer_id','order_status','order_purchase_timestamp',
            'order_approved_at','order_delivered_carrier_date',
            'order_delivered_customer_date','order_estimated_delivery_date',
            'delivery_days_actual','delivery_days_estimated','delay_days',
            'is_late','is_on_time','YearMonth','Year','Month','DayOfWeek',
            'order_value','freight_value','item_count','seller_id','product_id',
            'payment_value','payment_type','installments','review_score',
            'customer_state','customer_city','seller_state','seller_city',
            'product_category_name_english','product_weight_g','freight_ratio']

    sql = f"INSERT INTO cleaned_orders ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})"
    rows = [tuple(r) for r in df[cols].itertuples(index=False)]

    batch = 1000
    for i in range(0, len(rows), batch):
        cursor.executemany(sql, rows[i:i+batch])
        if i % 20000 == 0:
            print(f"  {i:,} / {len(rows):,} rows ...")
            conn.commit()
    conn.commit()
    print(f"  cleaned_orders: {len(rows):,} rows inserted.\n")

    # ── Load seller_scorecard ─────────────────────────────────
    print("Loading seller_scorecard ...")
    sc = pd.read_csv(f'{DATA_DIR}/seller_scorecard.csv')
    sc = sc.rename(columns={'rank': 'rank_position'})
    sc = sc.where(pd.notnull(sc), None)

    cursor.execute("TRUNCATE TABLE seller_scorecard")
    sc_cols = ['seller_id','seller_state','total_orders','total_revenue',
               'avg_review_score','late_orders','avg_delay_days',
               'avg_delivery_days','total_freight','late_rate_pct',
               'composite_score','rank_position','performance_tier']
    sc_sql = f"INSERT INTO seller_scorecard ({','.join(sc_cols)}) VALUES ({','.join(['%s']*len(sc_cols))})"
    sc_rows = [tuple(r) for r in sc[sc_cols].itertuples(index=False)]
    cursor.executemany(sc_sql, sc_rows)
    conn.commit()
    print(f"  seller_scorecard: {len(sc_rows):,} rows inserted.\n")

    cursor.close()
    conn.close()
    print("Done. All data loaded into MySQL.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',     default='localhost')
    parser.add_argument('--user',     default='root')
    parser.add_argument('--password', required=True)
    parser.add_argument('--database', default='olist_analytics')
    parser.add_argument('--port',     default=3306, type=int)
    args = parser.parse_args()
    load(args.host, args.user, args.password, args.database, args.port)
