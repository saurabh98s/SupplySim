{{ config(materialized='table') }}

WITH recursive_date_spine AS (
    -- Start date and end date for the time spine
    SELECT
        CAST('2023-01-01' AS DATE) AS date_spine -- Update start date as needed
    UNION ALL
    SELECT
        date_spine + 1
    FROM
        recursive_date_spine
    WHERE
        date_spine + 1 <= CAST('2030-12-31' AS DATE) -- Update end date as needed
)

SELECT
    date_spine AS time_spine_date,
    DATE_TRUNC('month', date_spine) AS time_spine_month,
    DATE_TRUNC('quarter', date_spine) AS time_spine_quarter,
    DATE_TRUNC('year', date_spine) AS time_spine_year
FROM
    recursive_date_spine
