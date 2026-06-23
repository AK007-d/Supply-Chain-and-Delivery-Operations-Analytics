"""
05_run_analytics.py
Supply Chain & Delivery Operations Analytics — Olist Brazilian E-commerce
---------------------------------------------------------------------------
Executes all 7 analytical queries from 05_mysql_analytics.sql using
SQLite (same logic, MySQL-compatible syntax).
Exports results to outputs/q*.csv for Power BI import.

Input  : data/cleaned_orders.csv, data/seller_scorecard.csv
Outputs: outputs/q1_monthly_volume.csv ... q7_pareto_analysis.csv
"""

import pandas as pd
import sqlite3
import os

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'input')
OUT_DIR  = os.path.join(os.path.dirname(__file__), '..', 'outputs')
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load into in-memory SQLite ────────────────────────────────
print("Loading data into database ...")
conn = sqlite3.connect(':memory:')
df   = pd.read_csv(f'{DATA_DIR}/cleaned_orders.csv')
sc   = pd.read_csv(f'{DATA_DIR}/seller_scorecard.csv')
sc   = sc.rename(columns={'rank': 'rank_position'})

df.to_sql('cleaned_orders',  conn, if_exists='replace', index=False)
sc.to_sql('seller_scorecard',conn, if_exists='replace', index=False)
print(f"  cleaned_orders  : {len(df):,} rows")
print(f"  seller_scorecard: {len(sc):,} rows\n")

def run(name, description, sql):
    print(f"Running {name}: {description}")
    result = pd.read_sql_query(sql, conn)
    result.to_csv(f'{OUT_DIR}/{name}.csv', index=False)
    print(result.head(5).to_string(index=False))
    print()
    return result

# ── Q1: Monthly Order Volume + MoM Growth ────────────────────
run('q1_monthly_volume', 'Monthly Order Volume + MoM Growth + On-Time Rate', """
    WITH monthly AS (
        SELECT
            YearMonth,
            COUNT(order_id)                                         AS total_orders,
            SUM(is_on_time)                                         AS on_time_orders,
            SUM(is_late)                                            AS late_orders,
            ROUND(SUM(is_on_time) * 100.0 / COUNT(order_id), 1)    AS on_time_rate_pct,
            ROUND(AVG(delay_days), 1)                               AS avg_delay_days,
            ROUND(SUM(order_value), 2)                              AS total_revenue,
            ROUND(AVG(review_score), 2)                             AS avg_review_score
        FROM cleaned_orders
        GROUP BY YearMonth
    )
    SELECT
        YearMonth,
        total_orders,
        on_time_orders,
        late_orders,
        on_time_rate_pct,
        avg_delay_days,
        total_revenue,
        avg_review_score,
        LAG(total_orders) OVER (ORDER BY YearMonth)  AS prev_month_orders,
        ROUND(
            (total_orders - LAG(total_orders) OVER (ORDER BY YearMonth))
            * 1.0 / LAG(total_orders) OVER (ORDER BY YearMonth) * 100
        , 1) AS MoM_order_growth_pct
    FROM monthly
    ORDER BY YearMonth
""")

# ── Q2: On-Time Delivery Rate by State ───────────────────────
run('q2_state_performance', 'SLA Breach Rate & On-Time Delivery by State', """
    SELECT
        customer_state,
        COUNT(order_id)                                             AS total_orders,
        SUM(is_late)                                                AS late_orders,
        ROUND(SUM(is_late) * 100.0 / COUNT(order_id), 1)           AS sla_breach_rate_pct,
        ROUND(SUM(is_on_time) * 100.0 / COUNT(order_id), 1)        AS on_time_rate_pct,
        ROUND(AVG(delivery_days_actual), 1)                         AS avg_delivery_days,
        ROUND(AVG(delay_days), 1)                                   AS avg_delay_days,
        ROUND(AVG(review_score), 2)                                 AS avg_review_score,
        ROUND(SUM(order_value), 2)                                  AS total_revenue,
        RANK() OVER (ORDER BY SUM(is_late) * 1.0
                     / COUNT(order_id) DESC)                        AS breach_rank
    FROM cleaned_orders
    WHERE customer_state IS NOT NULL
    GROUP BY customer_state
    ORDER BY sla_breach_rate_pct DESC
""")

# ── Q3: Seller Performance Ranking ───────────────────────────
run('q3_seller_ranking', 'Top and Bottom Sellers by Composite Score', """
    SELECT
        seller_id,
        seller_state,
        total_orders,
        ROUND(total_revenue, 2)     AS total_revenue,
        avg_review_score,
        late_rate_pct,
        avg_delay_days,
        composite_score,
        performance_tier,
        RANK()   OVER (ORDER BY composite_score DESC)   AS perf_rank,
        NTILE(4) OVER (ORDER BY composite_score DESC)   AS perf_quartile
    FROM seller_scorecard
    ORDER BY composite_score DESC
""")

# ── Q4: Freight Cost vs Delivery Speed by Category ───────────
run('q4_category_freight', 'Freight Cost vs Delivery Speed by Product Category', """
    WITH category_stats AS (
        SELECT
            product_category_name_english                           AS category,
            COUNT(order_id)                                         AS total_orders,
            ROUND(AVG(freight_value), 2)                            AS avg_freight_value,
            ROUND(AVG(order_value), 2)                              AS avg_order_value,
            ROUND(AVG(freight_value) * 100.0 / AVG(order_value), 1) AS freight_pct_of_order,
            ROUND(AVG(delivery_days_actual), 1)                     AS avg_delivery_days,
            ROUND(AVG(review_score), 2)                             AS avg_review_score,
            ROUND(SUM(is_late) * 100.0 / COUNT(order_id), 1)       AS late_rate_pct,
            ROUND(AVG(product_weight_g), 0)                         AS avg_weight_g
        FROM cleaned_orders
        WHERE product_category_name_english IS NOT NULL
        GROUP BY product_category_name_english
        HAVING COUNT(order_id) >= 50
    )
    SELECT
        category,
        total_orders,
        avg_freight_value,
        avg_order_value,
        freight_pct_of_order,
        avg_delivery_days,
        avg_review_score,
        late_rate_pct,
        avg_weight_g,
        RANK() OVER (ORDER BY freight_pct_of_order DESC)   AS freight_burden_rank,
        RANK() OVER (ORDER BY avg_delivery_days DESC)      AS slowest_delivery_rank
    FROM category_stats
    ORDER BY freight_pct_of_order DESC
""")

# ── Q5: Customer Satisfaction by Delivery Speed ───────────────
run('q5_satisfaction_speed', 'Customer Satisfaction by Delivery Speed Bucket', """
    WITH speed_buckets AS (
        SELECT
            CASE
                WHEN delivery_days_actual <= 7  THEN '1_Express (1-7 days)'
                WHEN delivery_days_actual <= 14 THEN '2_Standard (8-14 days)'
                WHEN delivery_days_actual <= 21 THEN '3_Slow (15-21 days)'
                ELSE                                 '4_Very Slow (22+ days)'
            END                                             AS delivery_bucket,
            COUNT(order_id)                                 AS orders,
            ROUND(AVG(review_score), 2)                     AS avg_review,
            ROUND(SUM(is_late) * 100.0 / COUNT(order_id),1) AS late_rate_pct,
            ROUND(AVG(order_value), 2)                      AS avg_order_value,
            ROUND(AVG(freight_value), 2)                    AS avg_freight
        FROM cleaned_orders
        WHERE review_score IS NOT NULL
        GROUP BY delivery_bucket
    )
    SELECT
        delivery_bucket,
        orders,
        avg_review,
        late_rate_pct,
        avg_order_value,
        avg_freight,
        RANK() OVER (ORDER BY avg_review DESC) AS satisfaction_rank
    FROM speed_buckets
    ORDER BY delivery_bucket
""")

# ── Q6: SLA Breach Heatmap State x Quarter ───────────────────
run('q6_breach_heatmap', 'SLA Breach Rate by State across Quarters', """
    SELECT
        customer_state,
        ROUND(SUM(CASE WHEN YearMonth BETWEEN '2017-01' AND '2017-03'
                       THEN is_late ELSE 0 END) * 100.0
              / NULLIF(SUM(CASE WHEN YearMonth BETWEEN '2017-01' AND '2017-03'
                                THEN 1 ELSE 0 END), 0), 1) AS breach_Q1_2017,
        ROUND(SUM(CASE WHEN YearMonth BETWEEN '2017-04' AND '2017-06'
                       THEN is_late ELSE 0 END) * 100.0
              / NULLIF(SUM(CASE WHEN YearMonth BETWEEN '2017-04' AND '2017-06'
                                THEN 1 ELSE 0 END), 0), 1) AS breach_Q2_2017,
        ROUND(SUM(CASE WHEN YearMonth BETWEEN '2017-07' AND '2017-09'
                       THEN is_late ELSE 0 END) * 100.0
              / NULLIF(SUM(CASE WHEN YearMonth BETWEEN '2017-07' AND '2017-09'
                                THEN 1 ELSE 0 END), 0), 1) AS breach_Q3_2017,
        ROUND(SUM(CASE WHEN YearMonth BETWEEN '2017-10' AND '2017-12'
                       THEN is_late ELSE 0 END) * 100.0
              / NULLIF(SUM(CASE WHEN YearMonth BETWEEN '2017-10' AND '2017-12'
                                THEN 1 ELSE 0 END), 0), 1) AS breach_Q4_2017,
        ROUND(SUM(CASE WHEN YearMonth BETWEEN '2018-01' AND '2018-03'
                       THEN is_late ELSE 0 END) * 100.0
              / NULLIF(SUM(CASE WHEN YearMonth BETWEEN '2018-01' AND '2018-03'
                                THEN 1 ELSE 0 END), 0), 1) AS breach_Q1_2018,
        ROUND(SUM(CASE WHEN YearMonth BETWEEN '2018-04' AND '2018-06'
                       THEN is_late ELSE 0 END) * 100.0
              / NULLIF(SUM(CASE WHEN YearMonth BETWEEN '2018-04' AND '2018-06'
                                THEN 1 ELSE 0 END), 0), 1) AS breach_Q2_2018,
        COUNT(order_id)                                     AS total_orders,
        ROUND(SUM(is_late) * 100.0 / COUNT(order_id), 1)   AS overall_breach_pct
    FROM cleaned_orders
    WHERE customer_state IS NOT NULL
    GROUP BY customer_state
    ORDER BY overall_breach_pct DESC
""")

# ── Q7: Revenue Concentration — Pareto ───────────────────────
run('q7_pareto_analysis', 'Revenue Concentration by Seller (Pareto)', """
    WITH seller_rev AS (
        SELECT
            seller_id,
            seller_state,
            COUNT(order_id)                                     AS total_orders,
            ROUND(SUM(order_value), 2)                          AS total_revenue,
            ROUND(AVG(review_score), 2)                         AS avg_review,
            ROUND(SUM(is_late) * 100.0 / COUNT(order_id), 1)   AS late_rate_pct
        FROM cleaned_orders
        WHERE seller_id IS NOT NULL
        GROUP BY seller_id, seller_state
    )
    SELECT
        seller_id,
        seller_state,
        total_orders,
        total_revenue,
        avg_review,
        late_rate_pct,
        RANK() OVER (ORDER BY total_revenue DESC)               AS revenue_rank,
        ROUND(
            PERCENT_RANK() OVER (ORDER BY total_revenue) * 100
        , 1)                                                    AS revenue_percentile,
        ROUND(
            SUM(total_revenue) OVER (ORDER BY total_revenue DESC
                                     ROWS BETWEEN UNBOUNDED PRECEDING
                                     AND CURRENT ROW)
            * 100.0 / SUM(total_revenue) OVER ()
        , 1)                                                    AS cumulative_revenue_share_pct
    FROM seller_rev
    ORDER BY total_revenue DESC
    LIMIT 50
""")

conn.close()
print("[05] All 7 queries complete. Results exported to outputs/")
