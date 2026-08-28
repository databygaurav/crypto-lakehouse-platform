import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def _safe_path_component(value, name):
    value = str(value)

    if (
        not value
        or value in {".", ".."}
        or Path(value).name != value
    ):
        raise ValueError(f"Invalid {name}: {value!r}")

    return value


class LocalStorage:

    def __init__(self, base_path="data/raw"):
        self.base_path = Path(base_path)

    def save_json(
        self,
        data,
        source,
        data_type,
        symbol=None
    ):
        now = datetime.now(timezone.utc)
        source = _safe_path_component(source, "source")
        data_type = _safe_path_component(
            data_type,
            "data_type"
        )

        folder = self.base_path / source / data_type

        if symbol:
            folder = folder / _safe_path_component(
                symbol,
                "symbol"
            )

        folder.mkdir(parents=True, exist_ok=True)

        filename = (
            f"{data_type}_"
            f"{now.strftime('%Y%m%dT%H%M%S_%fZ')}_"
            f"{uuid4().hex[:8]}.json"
        )
        file_path = folder / filename

        with file_path.open("x", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        return file_path
