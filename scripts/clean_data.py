import polars as pl
from pathlib import Path

# resolve paths relative to the project root (one level up from this script)
project_root = Path(__file__).resolve().parent.parent
raw_dir = project_root / "raw"
raw_dir.mkdir(exist_ok=True)

df = pl.read_csv('hf://datasets/imbalet/used_cars/dataset.csv')

df.write_csv(raw_dir / "used_cars.csv")

print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.head(10))
print(df.null_count())

pl.Config.set_tbl_cols(-1)  # show all columns, no truncation

print(df.null_count())
print(df["price"].describe())
print(df["mark"].n_unique(), df["region"].n_unique())