{% snapshot live_data_snapshot %}

{{
    config(
        target_database='DEV',
        target_schema='SNAPSHOTS',
        unique_key='SKU',
        strategy='timestamp',
        updated_at='LAST_MODIFIED',
    )
}}

SELECT * FROM {{ source('live', 'live_data') }}

{% endsnapshot %}
