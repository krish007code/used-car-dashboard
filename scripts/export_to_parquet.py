import duckdb
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
db_path = project_root / "used_car_dashboard" / "dev.duckdb"
exports_dir = project_root / "exports"
exports_dir.mkdir(exist_ok=True)

con = duckdb.connect(str(db_path), read_only=True)

marts = [
    "mart_market_overview",
    "mart_brand_performance",
    "mart_geography",
    "mart_value_drivers",
]

for mart in marts:
    out_path = exports_dir / f"{mart}.parquet"
    con.execute(f"COPY main.{mart} TO '{out_path}' (FORMAT PARQUET)")
    print(f"Exported {mart} -> {out_path}")

con.close()