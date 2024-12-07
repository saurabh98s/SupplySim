{{ config(materialized='table') }}

SELECT
    SKU,
    SUM(NUMBER_OF_PRODUCTS_SOLD) AS total_units_sold,
    SUM(NUMBER_OF_PRODUCTS_SOLD * PRICE) AS total_revenue,
    SUM(COSTS) AS total_costs,
    (SUM(NUMBER_OF_PRODUCTS_SOLD * PRICE) - SUM(COSTS)) AS total_profit
FROM {{ ref('sales_data') }}
GROUP BY SKU
ORDER BY total_profit DESC
