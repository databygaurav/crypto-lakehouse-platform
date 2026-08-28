from datetime import datetime, timedelta


# Binance endpoints that allow up to 90 days
# are queried in 89-day chunks to stay safely
# below the limit.
MAX_WINDOW_DAYS = 89


# C2C history accepts a maximum 30-day interval.
P2P_MAX_WINDOW_DAYS = 30


# Convert history also accepts a maximum 30-day interval.
CONVERT_MAX_WINDOW_DAYS = 30


# Universal transfer history is limited to
# approximately the latest 6 months.
TRANSFER_LOOKBACK_DAYS = 180


def datetime_to_ms(dt: datetime) -> int:
    """
    Convert a timezone-aware datetime to
    Unix timestamp in milliseconds.
    """

    if dt.tzinfo is None:
        raise ValueError(
            "datetime must be timezone-aware"
        )

    return int(
        dt.timestamp() * 1000
    )


def generate_time_windows(
    start_time: datetime,
    end_time: datetime
):
    """
    Split a large date range into Binance-safe
    windows.
    """

    return generate_non_overlapping_time_windows(
        start_time=start_time,
        end_time=end_time,
        max_window_days=MAX_WINDOW_DAYS
    )


def generate_non_overlapping_time_windows(
    start_time: datetime,
    end_time: datetime,
    max_window_days: int
):
    """
    Split a range into non-overlapping timestamp windows.

    Binance treats both timestamp bounds as inclusive,
    so each window ends one millisecond before the next
    window begins.
    """

    if max_window_days < 1:
        raise ValueError(
            "max_window_days must be at least 1"
        )

    if start_time.tzinfo is None:
        raise ValueError(
            "start_time must be timezone-aware"
        )

    if end_time.tzinfo is None:
        raise ValueError(
            "end_time must be timezone-aware"
        )

    if start_time >= end_time:
        raise ValueError(
            "start_time must be before end_time"
        )

    windows = []
    current_start = start_time

    while current_start < end_time:
        next_start = min(
            current_start
            + timedelta(days=max_window_days),
            end_time
        )

        windows.append(
            {
                "start_time": datetime_to_ms(
                    current_start
                ),
                "end_time": (
                    datetime_to_ms(next_start) - 1
                )
            }
        )

        current_start = next_start

    return windows


def generate_p2p_time_windows(
    start_time: datetime,
    end_time: datetime
):
    """Generate Binance-safe C2C history windows."""

    return generate_non_overlapping_time_windows(
        start_time=start_time,
        end_time=end_time,
        max_window_days=P2P_MAX_WINDOW_DAYS
    )


def generate_convert_time_windows(
    start_time: datetime,
    end_time: datetime
):
    """Generate Binance-safe Convert history windows."""

    return generate_non_overlapping_time_windows(
        start_time=start_time,
        end_time=end_time,
        max_window_days=CONVERT_MAX_WINDOW_DAYS
    )


def get_transfer_start_time(
    end_time: datetime
) -> datetime:
    """
    Calculate the earliest date that should
    be queried for Universal Transfer history.
    """

    if end_time.tzinfo is None:
        raise ValueError(
            "end_time must be timezone-aware"
        )

    return (
        end_time
        - timedelta(
            days=TRANSFER_LOOKBACK_DAYS
        )
    )


def fetch_klines_history(
    get_klines,
    symbol,
    interval,
    start_time,
    end_time,
    limit=1000
):
    """
    Fetch historical Binance klines using pagination.

    Parameters
    ----------
    get_klines:
        Function that calls BinanceClient.get_klines()

    symbol:
        Binance trading pair, e.g. BTCUSDT

    interval:
        Kline interval, e.g. 1m, 5m, 1h, 1d

    start_time:
        Unix timestamp in milliseconds

    end_time:
        Unix timestamp in milliseconds

    limit:
        Maximum candles per API request.
    """

    if start_time >= end_time:
        raise ValueError(
            "start_time must be before end_time"
        )

    all_klines = []

    current_start = start_time

    while current_start < end_time:

        klines = get_klines(
            symbol=symbol,
            interval=interval,
            start_time=current_start,
            end_time=end_time,
            limit=limit
        )

        if not klines:
            break

        all_klines.extend(
            klines
        )

        last_close_time = klines[-1][6]

        print(
            f"{symbol}: "
            f"Fetched {len(klines)} candles "
            f"(total: {len(all_klines)})"
        )

        # We have reached the requested end.
        if last_close_time >= end_time:
            break

        next_start = (
            last_close_time + 1
        )

        # Safety check.
        if next_start <= current_start:
            raise RuntimeError(
                "Kline pagination did not advance."
            )

        current_start = next_start

    return all_klines
