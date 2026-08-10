import json 
import pyarrow as pa
import pyarrow.parquet as pq

def json_to_parquet(json_file,parquet_file):
    # Read JSON
    with open(json_file,"r",encoding="utf-8") as file:
        data = json.load(file)

    # Convert Python data to Arrow table
    table = pa.Table.from_pylist(data)

    # Write Parquet
    pq.write_table(
        table,
        parquet_file
    )

    print(f"Parquet saved to: {parquet_file}")