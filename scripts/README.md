# Manual integration checks

These scripts call live Binance or AWS APIs and are intentionally excluded
from automated test discovery. Run them individually only when you want to
inspect real account data. Never paste their output into public logs or issues.

The automated, offline test suite lives in `tests/`.
