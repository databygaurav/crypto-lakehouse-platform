import pyarrow.parquet as pq


parquet_file = (
    "data/processed/binance/trades/"
    "BTCUSDT/year=2026/month=08/day=10/"
    "trades_20260810_195412.parquet"
)


table = pq.read_table(parquet_file)

print("Columns:")
print(table.column_names)

print("\nData:")
print(table.to_pandas())