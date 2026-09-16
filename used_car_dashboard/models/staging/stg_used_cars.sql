with source as (
    select * from read_parquet('{{ var("clean_data_path") }}')
),

staged as (
    select
        owners,
        year,
        price_rub,
        region,
        country,
        mileage,
        mark,
        model,
        complectation,
        steering_wheel,
        gear_type,
        engine,
        transmission,
        power,
        displacement,
        color,
        body_type_type,
        case
            when super_gen_name is null then 'Not specified'
            else super_gen_name
        end as super_gen_name,
        super_gen_year_from,
        super_gen_year_to,
        case
            when super_gen_year_to is null then true
            else false
        end as is_current_generation
    from source
    where country = 'Russia'
)

select * from staged