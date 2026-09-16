with staged as (
    select * from {{ ref('stg_used_cars') }}
),

by_region as (
    select
        region,
        count(*) as listing_count,
        avg(price_rub) as avg_price_rub,
        median(price_rub) as median_price_rub,
        avg(mileage) as avg_mileage
    from staged
    group by region
)

select * from by_region