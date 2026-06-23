-- ============================================================
-- 05_mysql_analytics.sql
-- Supply Chain & Delivery Operations Analytics — Olist
-- ============================================================
-- 7 business-critical queries covering:
--   Q1  Monthly Order Volume + MoM Growth
--   Q2  On-Time Delivery Rate by State
--   Q3  Top & Bottom Sellers by Composite Score
--   Q4  Freight Cost vs Delivery Speed by Category
--   Q5  Customer Satisfaction by Product Category
--   Q6  SLA Breach Heatmap: State x Month
--   Q7  Revenue Concentration by Seller (Pareto)
--
-- Syntax : MySQL 8.0+  (CTEs, window functions, LAG, RANK, NTILE)
-- Usage  : mysql -u root -p olist_analytics < scripts/05_mysql_analytics.sql
-- ============================================================

USE olist_analytics;

-- ════════════════════════════════════════════════════════════
-- Q1: Monthly Order Volume + MoM Growth + On-Time Rate
-- Window: LAG() to compare each month vs prior month
-- ════════════════════════════════════════════════════════════
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
    LAG(total_orders)   OVER (ORDER BY YearMonth)   AS prev_month_orders,
    ROUND(
        (total_orders - LAG(total_orders) OVER (ORDER BY YearMonth))
        * 1.0 / LAG(total_orders) OVER (ORDER BY YearMonth) * 100
    , 1)                                            AS MoM_order_growth_pct,
    LAG(on_time_rate_pct) OVER (ORDER BY YearMonth) AS prev_on_time_rate
FROM monthly
ORDER BY YearMonth;


-- ════════════════════════════════════════════════════════════
-- Q2: On-Time Delivery Rate & SLA Breach Rate by State
-- Window: RANK() on breach rate, DENSE_RANK() on review score
-- ════════════════════════════════════════════════════════════
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
    RANK()       OVER (ORDER BY SUM(is_late) * 1.0
                       / COUNT(order_id) DESC)                  AS breach_rank,
    DENSE_RANK() OVER (ORDER BY AVG(review_score) ASC)          AS satisfaction_rank
FROM cleaned_orders
WHERE customer_state IS NOT NULL
GROUP BY customer_state
ORDER BY sla_breach_rate_pct DESC;


-- ════════════════════════════════════════════════════════════
-- Q3: Top 25 and Bottom 25 Sellers by Composite Score
-- Window: RANK(), NTILE(4) for performance quartile
-- ════════════════════════════════════════════════════════════
WITH ranked_sellers AS (
    SELECT
        seller_id,
        seller_state,
        total_orders,
        ROUND(total_revenue, 2)     AS total_revenue,
        avg_review_score,
        late_rate_pct,
        avg_delay_days,
        avg_delivery_days,
        composite_score,
        performance_tier,
        RANK()   OVER (ORDER BY composite_score DESC)   AS perf_rank,
        NTILE(4) OVER (ORDER BY composite_score DESC)   AS perf_quartile
    FROM seller_scorecard
)
SELECT *
FROM ranked_sellers
WHERE perf_rank <= 25 OR perf_rank > (SELECT COUNT(*) FROM seller_scorecard) - 25
ORDER BY composite_score DESC;


-- ════════════════════════════════════════════════════════════
-- Q4: Freight Cost vs Delivery Speed by Product Category
-- Window: RANK() on freight burden, RANK() on delivery speed
-- ════════════════════════════════════════════════════════════
WITH category_stats AS (
    SELECT
        product_category_name_english                           AS category,
        COUNT(order_id)                                         AS total_orders,
        ROUND(AVG(freight_value), 2)                            AS avg_freight_value,
        ROUND(AVG(order_value), 2)                              AS avg_order_value,
        ROUND(AVG(freight_value) * 100.0
              / AVG(order_value), 1)                            AS freight_pct_of_order,
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
    RANK() OVER (ORDER BY freight_pct_of_order DESC)    AS freight_burden_rank,
    RANK() OVER (ORDER BY avg_delivery_days DESC)       AS slowest_delivery_rank,
    RANK() OVER (ORDER BY late_rate_pct DESC)           AS highest_late_rank
FROM category_stats
ORDER BY freight_pct_of_order DESC;


-- ════════════════════════════════════════════════════════════
-- Q5: Customer Satisfaction Score by State x Delivery Speed
-- Window: RANK() OVER (PARTITION BY state)
-- Shows which delivery speed buckets drive best satisfaction
-- ════════════════════════════════════════════════════════════
WITH speed_buckets AS (
    SELECT
        customer_state,
        CASE
            WHEN delivery_days_actual <= 7  THEN '1_Express (1-7 days)'
            WHEN delivery_days_actual <= 14 THEN '2_Standard (8-14 days)'
            WHEN delivery_days_actual <= 21 THEN '3_Slow (15-21 days)'
            ELSE                                 '4_Very Slow (22+ days)'
        END                                             AS delivery_bucket,
        COUNT(order_id)                                 AS orders,
        ROUND(AVG(review_score), 2)                     AS avg_review,
        ROUND(SUM(is_late) * 100.0 / COUNT(order_id),1) AS late_rate_pct
    FROM cleaned_orders
    WHERE customer_state IS NOT NULL
      AND review_score IS NOT NULL
    GROUP BY customer_state, delivery_bucket
)
SELECT
    customer_state,
    delivery_bucket,
    orders,
    avg_review,
    late_rate_pct,
    RANK() OVER (
        PARTITION BY customer_state
        ORDER BY avg_review DESC
    ) AS satisfaction_rank_within_state
FROM speed_buckets
ORDER BY customer_state, delivery_bucket;


-- ════════════════════════════════════════════════════════════
-- Q6: SLA Breach Heatmap — State x Month
-- Conditional aggregation for pivot-style output
-- ════════════════════════════════════════════════════════════
SELECT
    customer_state,
    ROUND(SUM(CASE WHEN YearMonth LIKE '2017-01%' THEN is_late END)
          * 100.0 / NULLIF(SUM(CASE WHEN YearMonth LIKE '2017-01%' THEN 1 END), 0), 1) AS breach_2017_01,
    ROUND(SUM(CASE WHEN YearMonth LIKE '2017-04%' THEN is_late END)
          * 100.0 / NULLIF(SUM(CASE WHEN YearMonth LIKE '2017-04%' THEN 1 END), 0), 1) AS breach_2017_04,
    ROUND(SUM(CASE WHEN YearMonth LIKE '2017-07%' THEN is_late END)
          * 100.0 / NULLIF(SUM(CASE WHEN YearMonth LIKE '2017-07%' THEN 1 END), 0), 1) AS breach_2017_07,
    ROUND(SUM(CASE WHEN YearMonth LIKE '2017-10%' THEN is_late END)
          * 100.0 / NULLIF(SUM(CASE WHEN YearMonth LIKE '2017-10%' THEN 1 END), 0), 1) AS breach_2017_10,
    ROUND(SUM(CASE WHEN YearMonth LIKE '2018-01%' THEN is_late END)
          * 100.0 / NULLIF(SUM(CASE WHEN YearMonth LIKE '2018-01%' THEN 1 END), 0), 1) AS breach_2018_01,
    ROUND(SUM(CASE WHEN YearMonth LIKE '2018-04%' THEN is_late END)
          * 100.0 / NULLIF(SUM(CASE WHEN YearMonth LIKE '2018-04%' THEN 1 END), 0), 1) AS breach_2018_04,
    ROUND(SUM(CASE WHEN YearMonth LIKE '2018-07%' THEN is_late END)
          * 100.0 / NULLIF(SUM(CASE WHEN YearMonth LIKE '2018-07%' THEN 1 END), 0), 1) AS breach_2018_07,
    COUNT(order_id)                                                                      AS total_orders,
    ROUND(SUM(is_late) * 100.0 / COUNT(order_id), 1)                                   AS overall_breach_pct
FROM cleaned_orders
WHERE customer_state IS NOT NULL
GROUP BY customer_state
ORDER BY overall_breach_pct DESC;


-- ════════════════════════════════════════════════════════════
-- Q7: Revenue Concentration by Seller (Pareto Analysis)
-- Window: SUM() OVER() for cumulative revenue share
--         PERCENT_RANK() for seller revenue percentile
-- ════════════════════════════════════════════════════════════
WITH seller_rev AS (
    SELECT
        seller_id,
        seller_state,
        COUNT(order_id)                                         AS total_orders,
        ROUND(SUM(order_value), 2)                              AS total_revenue,
        ROUND(AVG(review_score), 2)                             AS avg_review,
        ROUND(SUM(is_late) * 100.0 / COUNT(order_id), 1)       AS late_rate_pct
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
    RANK()   OVER (ORDER BY total_revenue DESC)                 AS revenue_rank,
    ROUND(
        PERCENT_RANK() OVER (ORDER BY total_revenue) * 100
    , 1)                                                        AS revenue_percentile,
    ROUND(
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC
                                 ROWS BETWEEN UNBOUNDED PRECEDING
                                 AND CURRENT ROW)
        * 100.0 / SUM(total_revenue) OVER ()
    , 1)                                                        AS cumulative_revenue_share_pct
FROM seller_rev
ORDER BY total_revenue DESC
LIMIT 50;
