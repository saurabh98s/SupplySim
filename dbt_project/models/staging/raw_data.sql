{{ config(materialized='table') }}

SELECT 
    *,
    -- Calculate average revenue per product
    CASE 
        WHEN NUMBER_OF_PRODUCTS_SOLD > 0 THEN REVENUE_GENERATED / NUMBER_OF_PRODUCTS_SOLD
        ELSE NULL
    END AS avg_revenue_per_product,
    
    -- Restock flag based on stock levels
    CASE
        WHEN STOCK_LEVELS < (10 * NUMBER_OF_PRODUCTS_SOLD) THEN 1
        ELSE 0
    END AS restock_flag
    
FROM {{ source('raw', 'supply_chain_data') }}
WHERE NUMBER_OF_PRODUCTS_SOLD IS NOT NULL
  AND STOCK_LEVELS IS NOT NULL
  AND PRICE > 0