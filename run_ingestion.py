"""Beginner-friendly command for starting Binance ingestion.

Run locally only:
    python run_ingestion.py --local-only

Run locally and upload to S3:
    python run_ingestion.py
"""

from ingestion.binance_ingestion import main


if __name__ == "__main__":
    main()
