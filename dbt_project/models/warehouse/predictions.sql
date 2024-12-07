{{ config(materialized='table') }}

WITH forecast_data AS (
    SELECT
        SKU,
        DATEADD('week', 1, MAX(DATE_INSERT)) AS forecast_week,
        AVG(NUMBER_OF_PRODUCTS_SOLD) AS forecast_units_sold
    FROM {{ ref('sales_data') }}
    WHERE NUMBER_OF_PRODUCTS_SOLD > 0
    GROUP BY SKU
)

SELECT
    fd.SKU,
    fd.forecast_week,
    fd.forecast_units_sold,
    r.PRODUCT_TYPE,
    r.AVAILABILITY,
    r.STOCK_LEVELS
FROM forecast_data fd
LEFT JOIN {{ ref('raw_data') }} r
    ON fd.SKU = r.SKU
WHERE r.AVAILABILITY > 0
