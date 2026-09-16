with staged as (
    select * from {{ ref('stg_used_cars') }}
),

by_mark_model as (
    select
        mark,
        model,
        super_gen_name,
        is_current_generation,
        count(*) as listing_count,
        avg(price_rub) as avg_price_rub,
        median(price_rub) as median_price_rub,
        min(price_rub) as min_price_rub,
        max(price_rub) as max_price_rub,
        avg(mileage) as avg_mileage
    from staged
    group by mark, model, super_gen_name, is_current_generation
)

select * from by_mark_model