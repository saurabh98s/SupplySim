{{ config(materialized='table') }}

WITH historical_sales AS (
    SELECT
        DATE_TRUNC('week', DATE_INSERT) AS sales_week,
        SKU,
        SUM(NUMBER_OF_PRODUCTS_SOLD) AS total_units_sold
    FROM {{ ref('sales_data') }}
    WHERE DATE_INSERT IS NOT NULL
      AND DATE_PART('year', DATE_INSERT) BETWEEN 1900 AND 2100
    GROUP BY 1, 2
)

SELECT
    SKU,
    DATEADD('week', 1, MAX(sales_week)) AS forecast_week,
    AVG(total_units_sold) AS forecast_units_sold
FROM historical_sales
GROUP BY SKU
