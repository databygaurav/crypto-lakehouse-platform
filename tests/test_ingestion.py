import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from ingestion.binance_ingestion import run_ingestion
from storage.local_storage import LocalStorage


class IngestionTests(unittest.TestCase):

    def test_run_is_explicit_and_supports_local_only_mode(self):
        client = Mock()
        client.get_account.return_value = {"balances": []}
        client.get_all_trades.return_value = []
        client.get_all_convert_trades.return_value = []
        client.get_all_p2p_transactions.return_value = []
        client.get_all_deposits.return_value = []
        client.get_all_withdrawals.return_value = []
        client.get_all_transfers.return_value = []
        client.get_klines.return_value = []

        start = datetime(
            2026,
            8,
            1,
            tzinfo=timezone.utc
        )

        with tempfile.TemporaryDirectory() as directory:
            outputs = run_ingestion(
                client=client,
                local_storage=LocalStorage(directory),
                history_start=start,
                history_end=start + timedelta(days=1),
                trading_pairs=("SOLUSDT",),
                transfer_types=("MAIN_UMFUTURE",),
                upload_to_s3=False
            )

        self.assertIn("account", outputs)
        self.assertIn("trades:SOLUSDT", outputs)
        self.assertIn("convert_trades", outputs)
        self.assertIn("ingestion_manifest", outputs)
        client.get_all_trades.assert_called_once_with(
            symbol="SOLUSDT"
        )


if __name__ == "__main__":
    unittest.main()
