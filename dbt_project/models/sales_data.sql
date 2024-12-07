{{ config(materialized='table') }}

SELECT
    TO_TIMESTAMP_NTZ(ld.DATE_INSERT) AS DATE_INSERT,
    ld.SKU,
    ld.PRODUCT_TYPE,
    ld.PRICE,
    ld.NUMBER_OF_PRODUCTS_SOLD,
    ld.STOCK_LEVELS,
    ld.COSTS
FROM {{ source('live', 'live_data') }} ld
WHERE ld.DATE_INSERT IS NOT NULL
  AND DATE_PART('year', TO_TIMESTAMP_NTZ(ld.DATE_INSERT)) BETWEEN 1900 AND 2100

UNION ALL

SELECT
    wp.DATE_INSERT,
    wp.SKU,
    NULL AS PRODUCT_TYPE,
    NULL AS PRICE,
    wp.NUMBER_OF_PRODUCTS_SOLD,
    wp.STOCK_LEVELS,
    wp.COSTS
FROM {{ source('live', 'weekly_predictions') }} wp
WHERE wp.DATE_INSERT IS NOT NULL
  AND DATE_PART('year', wp.DATE_INSERT) BETWEEN 1900 AND 2100
