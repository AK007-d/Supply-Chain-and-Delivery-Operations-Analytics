-- ============================================================
-- 00_mysql_setup.sql
-- Supply Chain & Delivery Operations Analytics — Olist
-- ============================================================
-- Run this FIRST to create the schema and tables.
-- Usage: mysql -u root -p < scripts/00_mysql_setup.sql
-- Tested on: MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS olist_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE olist_analytics;

-- ── Drop if re-running ────────────────────────────────────────
DROP TABLE IF EXISTS seller_scorecard;
DROP TABLE IF EXISTS category_performance;
DROP TABLE IF EXISTS state_performance;
DROP TABLE IF EXISTS delivery_performance;
DROP TABLE IF EXISTS cleaned_orders;

-- ── Core orders table ─────────────────────────────────────────
CREATE TABLE cleaned_orders (
    order_id                        VARCHAR(50)     NOT NULL PRIMARY KEY,
    customer_id                     VARCHAR(50)     NOT NULL,
    order_status                    VARCHAR(20),
    order_purchase_timestamp        DATETIME        NOT NULL,
    order_approved_at               DATETIME,
    order_delivered_carrier_date    DATETIME,
    order_delivered_customer_date   DATETIME,
    order_estimated_delivery_date   DATETIME,
    delivery_days_actual            INT,
    delivery_days_estimated         INT,
    delay_days                      FLOAT,
    is_late                         TINYINT         NOT NULL DEFAULT 0,
    is_on_time                      TINYINT         NOT NULL DEFAULT 1,
    YearMonth                       VARCHAR(7)      NOT NULL,
    Year                            SMALLINT        NOT NULL,
    Month                           TINYINT         NOT NULL,
    DayOfWeek                       VARCHAR(10),
    order_value                     DECIMAL(12,2),
    freight_value                   DECIMAL(10,2),
    item_count                      TINYINT,
    seller_id                       VARCHAR(50),
    product_id                      VARCHAR(50),
    payment_value                   DECIMAL(12,2),
    payment_type                    VARCHAR(30),
    installments                    TINYINT,
    review_score                    FLOAT,
    customer_state                  CHAR(2),
    customer_city                   VARCHAR(100),
    seller_state                    CHAR(2),
    seller_city                     VARCHAR(100),
    product_category_name_english   VARCHAR(100),
    product_weight_g                FLOAT,
    freight_ratio                   FLOAT,

    INDEX idx_seller        (seller_id),
    INDEX idx_customer_state(customer_state),
    INDEX idx_yearmonth     (YearMonth),
    INDEX idx_category      (product_category_name_english),
    INDEX idx_is_late       (is_late),
    INDEX idx_purchase_ts   (order_purchase_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── Seller scorecard table ────────────────────────────────────
CREATE TABLE seller_scorecard (
    seller_id           VARCHAR(50)     NOT NULL PRIMARY KEY,
    seller_state        CHAR(2),
    total_orders        INT,
    total_revenue       DECIMAL(12,2),
    avg_review_score    FLOAT,
    late_orders         INT,
    avg_delay_days      FLOAT,
    avg_delivery_days   FLOAT,
    total_freight       DECIMAL(12,2),
    late_rate_pct       FLOAT,
    composite_score     FLOAT,
    rank_position       INT,
    performance_tier    VARCHAR(20),

    INDEX idx_tier  (performance_tier),
    INDEX idx_score (composite_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT 'Schema created successfully.' AS Status;
