"""Project settings loaded from the local .env file."""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv


load_dotenv()

# Binance credentials are needed for private account-history endpoints.
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Giottus credentials 
GIOTTUS_API_KEY = os.getenv("GIOTTUS_API_KEY")
GIOTTUS_SECRET_KEY = os.getenv("GIOTTUS_SECRET_KEY")

# CoinDCX credentials are used only for the current-balance endpoint.
COINDCX_API_KEY = os.getenv("COINDCX_API_KEY")
COINDCX_SECRET_KEY = os.getenv("COINDCX_SECRET_KEY")

# S3 credentials are optional when your normal AWS login or IAM role is used.
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

# Change this date when you want ingestion to begin from another day.
BINANCE_HISTORY_START = datetime(
    2025,
    5,
    29,
    tzinfo=timezone.utc,
)
