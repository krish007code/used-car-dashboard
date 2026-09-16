    with staged as (
    select * from {{ ref('stg_used_cars') }}
),

final as (
    select
        price_rub,
        mileage,
        owners,
        steering_wheel,
        power,
        displacement,
        transmission,
        gear_type
    from staged
)

select * from final