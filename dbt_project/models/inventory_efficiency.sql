{{ config(materialized='table') }}

WITH weekly_sales AS (
    SELECT
        DATE_TRUNC('week', DATE_INSERT) AS sales_week,
        SKU,
        SUM(NUMBER_OF_PRODUCTS_SOLD) AS total_units_sold,
        AVG(STOCK_LEVELS) AS average_stock
    FROM {{ ref('sales_data') }}
    WHERE DATE_INSERT IS NOT NULL
      AND DATE_PART('year', DATE_INSERT) BETWEEN 1900 AND 2100
    GROUP BY 1, 2
)

SELECT
    SKU,
    AVG(average_stock) AS average_stock,
    SUM(total_units_sold) AS total_units_sold,
    SUM(total_units_sold) / NULLIF(SUM(average_stock), 0) AS inventory_turnover  -- Avoid division by zero
FROM weekly_sales
GROUP BY SKU
