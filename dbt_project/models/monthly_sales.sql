{{ config(materialized='table') }}

WITH daily_sales AS (
    SELECT
        DATE_TRUNC('day', DATE_INSERT) AS sales_date,
        SKU,
        NUMBER_OF_PRODUCTS_SOLD,
        STOCK_LEVELS,
        COSTS,
        PRICE
    FROM {{ ref('sales_data') }}
    WHERE DATE_INSERT IS NOT NULL
      AND DATE_PART('year', DATE_INSERT) BETWEEN 1900 AND 2100  -- Exclude invalid dates
)

SELECT
    DATE_TRUNC('month', sales_date) AS sales_month,
    SKU,
    SUM(NUMBER_OF_PRODUCTS_SOLD) AS total_products_sold,
    AVG(STOCK_LEVELS) AS average_stock_levels,
    SUM(COSTS) AS total_costs,
    AVG(PRICE) AS average_price,
    SUM(NUMBER_OF_PRODUCTS_SOLD * PRICE) AS total_revenue
FROM daily_sales
GROUP BY 1, 2
