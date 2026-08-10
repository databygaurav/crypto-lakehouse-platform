import json
from pathlib import Path
from datetime import datetime


class LocalStorage:

    def __init__(self, base_path="data/raw"):
        self.base_path = Path(base_path)

    def save_json(self, data, source, data_type, symbol=None):
        now = datetime.now()

        folder = (
            self.base_path
            / source
            / data_type
        )

        # Add trading pair folder if provided
        if symbol:
            folder = folder / symbol

        folder = (
            folder
            / f"year={now.year}"
            / f"month={now.month:02d}"
            / f"day={now.day:02d}"
        )

        folder.mkdir(parents=True, exist_ok=True)

        filename = (
            f"{data_type}_"
            f"{now.strftime('%Y%m%d_%H%M%S')}.json"
        )

        file_path = folder / filename

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        return file_path