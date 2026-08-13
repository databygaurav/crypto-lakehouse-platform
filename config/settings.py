import os
from datetime import datetime, timezone

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# BINANCE
# ============================================================

BINANCE_API_KEY = os.getenv(
    "BINANCE_API_KEY"
)

BINANCE_SECRET_KEY = os.getenv(
    "BINANCE_SECRET_KEY"
)


# ============================================================
# AWS
# ============================================================

AWS_ACCESS_KEY_ID = os.getenv(
    "AWS_ACCESS_KEY_ID"
)

AWS_SECRET_ACCESS_KEY = os.getenv(
    "AWS_SECRET_ACCESS_KEY"
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-south-1"
)

AWS_S3_BUCKET = os.getenv(
    "AWS_S3_BUCKET"
)


# ============================================================
# BINANCE HISTORY
# ============================================================

BINANCE_HISTORY_START = datetime(
    2026,
    1,
    1,
    tzinfo=timezone.utc
)


# ============================================================
# VALIDATION
# ============================================================

required_settings = {
    "BINANCE_API_KEY": BINANCE_API_KEY,
    "BINANCE_SECRET_KEY": BINANCE_SECRET_KEY,
    "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    "AWS_S3_BUCKET": AWS_S3_BUCKET,
}


missing_settings = [
    name
    for name, value in required_settings.items()
    if not value
]


if missing_settings:

    raise ValueError(
        "Missing required environment variables: "
        + ", ".join(missing_settings)
    )