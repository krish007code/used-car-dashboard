import polars as pl
from pathlib import Path
from tqdm import tqdm

project_root = Path(__file__).resolve().parent.parent
raw_path = project_root / "raw" / "used_cars.csv"
clean_dir = project_root / "clean"
clean_dir.mkdir(exist_ok=True)

# --- Region translation map ---
region_map = {
    "Приморский край": "Primorsky Krai",
    "Орловская область": "Oryol Oblast",
    "Калужская область": "Kaluga Oblast",
    "Москва и Московская область": "Moscow & Moscow Oblast",
    "Белгородская область": "Belgorod Oblast",
    "Санкт-Петербург и Ленинградская область": "Saint Petersburg & Leningrad Oblast",
    "Ставропольский край": "Stavropol Krai",
    "Волгоградская область": "Volgograd Oblast",
    "Саратовская область": "Saratov Oblast",
    "Челябинская область": "Chelyabinsk Oblast",
    "Ульяновская область": "Ulyanovsk Oblast",
    "Республика Татарстан": "Republic of Tatarstan",
    "Псковская область": "Pskov Oblast",
    "Ростовская область": "Rostov Oblast",
    "Республика Башкортостан": "Republic of Bashkortostan",
    "Красноярский край": "Krasnoyarsk Krai",
    "Самарская область": "Samara Oblast",
    "Тюменская область": "Tyumen Oblast",
    "Свердловская область": "Sverdlovsk Oblast",
    "Новосибирская область": "Novosibirsk Oblast",
    "Вологодская область": "Vologda Oblast",
    "Республика Хакасия": "Republic of Khakassia",
    "Краснодарский край": "Krasnodar Krai",
    "Нижегородская область": "Nizhny Novgorod Oblast",
    "Омская область": "Omsk Oblast",
    "Удмуртская Республика": "Udmurt Republic",
    "Воронежская область": "Voronezh Oblast",
    "Курская область": "Kursk Oblast",
    "Республика Крым": "Republic of Crimea",
    "Курганская область": "Kurgan Oblast",
    "Кемеровская область (Кузбасс)": "Kemerovo Oblast (Kuzbass)",
    "Ивановская область": "Ivanovo Oblast",
    "Тверская область": "Tver Oblast",
    "Республика Бурятия": "Republic of Buryatia",
    "Хабаровский край": "Khabarovsk Krai",
    "Иркутская область": "Irkutsk Oblast",
    "Брянская область": "Bryansk Oblast",
    "Республика Саха (Якутия)": "Republic of Sakha (Yakutia)",
    "Владимирская область": "Vladimir Oblast",
    "Ненецкий автономный округ": "Nenets Autonomous Okrug",
    "Ярославская область": "Yaroslavl Oblast",
    "Кабардино-Балкарская Республика": "Kabardino-Balkar Republic",
    "Пермский край": "Perm Krai",
    "Рязанская область": "Ryazan Oblast",
    "Республика Калмыкия": "Republic of Kalmykia",
    "Карачаево-Черкесская Республика": "Karachay-Cherkess Republic",
    "Чувашская Республика": "Chuvash Republic",
    "Смоленская область": "Smolensk Oblast",
    "Архангельская область": "Arkhangelsk Oblast",
    "Республика Мордовия": "Republic of Mordovia",
    "Новгородская область": "Novgorod Oblast",
    "Томская область": "Tomsk Oblast",
    "Кировская область": "Kirov Oblast",
    "Тульская область": "Tula Oblast",
    "Калининградская область": "Kaliningrad Oblast",
    "Республика Ингушетия": "Republic of Ingushetia",
    "Сахалинская область": "Sakhalin Oblast",
    "Республика Северная Осетия — Алания": "Republic of North Ossetia-Alania",
    "Астраханская область": "Astrakhan Oblast",
    "Алтайский край": "Altai Krai",
    "Амурская область": "Amur Oblast",
    "Пензенская область": "Penza Oblast",
    "Забайкальский край": "Zabaykalsky Krai",
    "Ханты-Мансийский автономный округ - Югра": "Khanty-Mansi Autonomous Okrug - Yugra",
    "Костромская область": "Kostroma Oblast",
    "Оренбургская область": "Orenburg Oblast",
    "Липецкая область": "Lipetsk Oblast",
    "Республика Дагестан": "Republic of Dagestan",
    "Камчатский край": "Kamchatka Krai",
    "Республика Марий Эл": "Mari El Republic",
    "Республика Адыгея": "Republic of Adygea",
    "Тамбовская область": "Tambov Oblast",
    "Мурманская область": "Murmansk Oblast",
    "Республика Коми": "Komi Republic",
    "Чеченская Республика": "Chechen Republic",
    "Республика Карелия": "Republic of Karelia",
    "Республика Тыва": "Republic of Tyva",
    "Ямало-Ненецкий автономный округ": "Yamalo-Nenets Autonomous Okrug",
    "Магаданская область": "Magadan Oblast",
    "Республика Алтай": "Altai Republic",
    "Витебская область": "Vitebsk Oblast",
    "Еврейская автономная область": "Jewish Autonomous Oblast",
    "Чукотский автономный округ": "Chukotka Autonomous Okrug",
    "Минская область": "Minsk Oblast",
    "Брестская область": "Brest Oblast",
    "Гомельская область": "Gomel Oblast",
    "Западно-Казахстанская область": "West Kazakhstan Oblast",
}

BELARUS_REGIONS = {"Vitebsk Oblast", "Minsk Oblast", "Brest Oblast", "Gomel Oblast"}
KAZAKHSTAN_REGIONS = {"West Kazakhstan Oblast"}

steps = [
    "Load raw CSV",
    "Fix 'nan'-string bug -> true nulls",
    "Translate region",
    "Add country column",
    "Clean super_gen_name",
    "Normalize mark casing",
    "Drop redundant columns",
    "Fill complectation nulls",
    "Rename price -> price_rub",
    "Cast categoricals",
    "Deduplicate rows",
    "Write Parquet",
]

pbar = tqdm(steps, desc="Cleaning pipeline")

# 1. Load
pbar.set_description(steps[0]); df = pl.read_csv(raw_path); pbar.update(0)
pbar.update(1)

# 2. Fix "nan"-string bug
pbar.set_description(steps[1])
str_cols = [c for c, dt in zip(df.columns, df.dtypes) if dt == pl.Utf8]
df = df.with_columns([
    pl.when(pl.col(c).str.to_lowercase() == "nan")
      .then(None)
      .otherwise(pl.col(c))
      .alias(c)
    for c in str_cols
])
pbar.update(1)

# 3. Translate region
pbar.set_description(steps[2])
df = df.with_columns(pl.col("region").replace(region_map).alias("region"))
pbar.update(1)

# 4. Country flag (Russia / Belarus / Kazakhstan)
pbar.set_description(steps[3])
df = df.with_columns(
    pl.when(pl.col("region").is_in(BELARUS_REGIONS)).then(pl.lit("Belarus"))
      .when(pl.col("region").is_in(KAZAKHSTAN_REGIONS)).then(pl.lit("Kazakhstan"))
      .otherwise(pl.lit("Russia"))
      .alias("country")
)
pbar.update(1)

# 5. super_gen_name cleanup
pbar.set_description(steps[4])
df = df.with_columns(
    pl.col("super_gen_name").str.replace("Рестайлинг", "Restyling").alias("super_gen_name")
)
pbar.update(1)

# 6. mark casing
pbar.set_description(steps[5])
df = df.with_columns(pl.col("mark").str.to_titlecase().alias("mark"))
pbar.update(1)

# 7. Drop redundant columns
pbar.set_description(steps[6])
df = df.drop(["body_type_name", "characteristics"])
pbar.update(1)

# 8. Fill complectation nulls
pbar.set_description(steps[7])
df = df.with_columns(pl.col("complectation").fill_null("Base/Unspecified"))
pbar.update(1)

# 9. Rename price
pbar.set_description(steps[8])
df = df.rename({"price": "price_rub"})
pbar.update(1)

# 10. Categoricals
pbar.set_description(steps[9])
df = df.with_columns([
    pl.col(c).cast(pl.Categorical)
    for c in ["steering_wheel", "gear_type", "engine", "transmission", "body_type_type", "country"]
])
pbar.update(1)

# 11. Dedup
pbar.set_description(steps[10])
before = df.height
df = df.unique()
dropped = before - df.height
pbar.update(1)

# 12. Write Parquet
pbar.set_description(steps[11])
out_path = clean_dir / "used_cars_clean.parquet"
df.write_parquet(out_path)
pbar.update(1)
pbar.close()

print(f"\nDropped {dropped} duplicate rows")
print(f"Final shape: {df.shape}")
print(f"Written to: {out_path}")
print(df.null_count())
print(df["country"].value_counts())