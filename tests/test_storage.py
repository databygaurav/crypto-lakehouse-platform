import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from storage.local_storage import LocalStorage
from storage.s3_storage import S3Storage


class LocalStorageTests(unittest.TestCase):

    def test_writes_unique_files_in_a_flat_dataset_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = LocalStorage(directory)
            first = storage.save_json(
                [{"id": 1}],
                source="binance",
                data_type="trades",
                symbol="SOLUSDT"
            )
            second = storage.save_json(
                [{"id": 2}],
                source="binance",
                data_type="trades",
                symbol="SOLUSDT"
            )

            self.assertNotEqual(first, second)
            self.assertEqual(
                first.parent,
                Path(directory) / "binance" / "trades" / "SOLUSDT"
            )
            self.assertNotIn("year=", first.as_posix())

            with Path(first).open("r", encoding="utf-8") as file:
                self.assertEqual(json.load(file), [{"id": 1}])

    def test_rejects_path_traversal_components(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = LocalStorage(directory)

            with self.assertRaisesRegex(ValueError, "Invalid symbol"):
                storage.save_json(
                    [],
                    source="binance",
                    data_type="trades",
                    symbol="../escape"
                )


class S3StorageTests(unittest.TestCase):

    def test_uses_injected_client_and_bucket(self):
        client = Mock()
        storage = S3Storage(
            bucket="test-bucket",
            s3_client=client
        )

        result = storage.upload_file(
            "local.json",
            "raw/local.json"
        )

        client.upload_file.assert_called_once_with(
            "local.json",
            "test-bucket",
            "raw/local.json"
        )
        self.assertEqual(result, "raw/local.json")


if __name__ == "__main__":
    unittest.main()
