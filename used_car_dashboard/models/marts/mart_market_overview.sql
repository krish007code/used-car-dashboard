with staged as (
    select * from {{ ref('stg_used_cars') }}
),

final as (
    select
        price_rub,
        year,
        body_type_type,
        (2026 - year) as vehicle_age_years,
        mark,
        model
    from staged
)

select * from final