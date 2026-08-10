import json
from pathlib import Path
from datetime import datetime

def load_trades(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        trades = json.load(file)

    return trades


def clean_trades(trades):
    cleaned_trades = []

    for trade in trades:
        trade_datetime = datetime.fromtimestamp(
            trade["time"] / 1000
        )
        cleaned_trade = {
            "symbol": trade["symbol"],
            "price": float(trade["price"]),
            "qty": float(trade["qty"]),
            "quoteQty": float(trade["quoteQty"]),
            "trade_value": round(float(trade["price"]) * float(trade["qty"]),8),
            "commission": float(trade["commission"]),
            "commissionAsset": trade["commissionAsset"],
            "time": trade["time"],
            "datetime": trade_datetime.isoformat(),
            "isBuyer": trade["isBuyer"],
        }

        cleaned_trades.append(cleaned_trade)

    return cleaned_trades


def save_processed_trades(trades, file_path):
    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            trades,
            file,
            indent=2
        )

    print("Processed trades saved to:", file_path)