{{ config(materialized='table') }}

WITH daily_variance AS (
    SELECT
        SKU,
        DATE_TRUNC('day', DATE_INSERT) AS sales_date,
        NUMBER_OF_PRODUCTS_SOLD
    FROM {{ ref('sales_data') }}
    WHERE DATE_INSERT IS NOT NULL
      AND DATE_PART('year', DATE_INSERT) BETWEEN 1900 AND 2100
)

SELECT
    SKU,
    ROUND(1.65 * STDDEV(NUMBER_OF_PRODUCTS_SOLD)) AS safety_stock_level  -- 95% service level
FROM daily_variance
GROUP BY SKU
