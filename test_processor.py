from processing.trade_processor import (
    load_trades,
    clean_trades,
    save_processed_trades,
)


file_path = "data/raw/binance/trades/year=2026/month=08/day=09/trades_20260809_215305.json"

# 1. Load raw trades
trades = load_trades(file_path)

# 2. Clean trades
cleaned_trades = clean_trades(trades)

# 3. Save processed trades
output_path = "data/processed/binance/trades/trades_cleaned.json"

save_processed_trades(
    cleaned_trades,
    output_path
)