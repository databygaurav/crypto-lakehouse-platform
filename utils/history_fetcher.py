from datetime import datetime, timedelta


# Binance endpoints that allow up to 90 days
# are queried in 89-day chunks to stay safely
# below the limit.
MAX_WINDOW_DAYS = 89

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

    return int(dt.timestamp() * 1000)


def generate_time_windows(
    start_time: datetime,
    end_time: datetime
):
    """
    Split a large date range into Binance-safe
    windows.
    """

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

        current_end = min(
            current_start
            + timedelta(days=MAX_WINDOW_DAYS),
            end_time
        )

        windows.append(
            {
                "start_time": datetime_to_ms(
                    current_start
                ),
                "end_time": datetime_to_ms(
                    current_end
                )
            }
        )

        current_start = current_end

    return windows


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
        - timedelta(days=TRANSFER_LOOKBACK_DAYS)
    )