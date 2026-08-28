# Crypto Lakehouse Platform

A portfolio data-engineering project that collects Binance account and market
history, stores immutable JSON files locally and in Amazon S3, and processes the
data in Databricks using a medallion architecture.

```text
Binance APIs
     |
     v
Python ingestion
     |
     +----> Local raw JSON
     |
     +----> Amazon S3
                |
                v
        Databricks Bronze
                |
                v
        Databricks Silver
                |
                v
          Gold analytics
```

## Project status

| Component | Status | Responsibility |
|---|---|---|
| Python ingestion | Complete | Downloads paginated Binance data and stores raw JSON |
| Local and S3 storage | Complete | Preserves source responses in dataset-specific folders |
| Databricks Bronze | Complete | Applies explicit schemas, lineage metadata, and record-level deduplication |
| Databricks Silver | In progress | Standardizes types and combines related transaction sources |
| Gold analytics | Planned | Portfolio positions, cost basis, and performance metrics |

## Data collected

- Binance account snapshots and balances
- Spot trade history for configured trading pairs
- Binance Convert transactions
- P2P BUY and SELL orders
- Deposits and withdrawals
- Universal account transfers
- Daily candlestick price history
- An ingestion manifest for each completed run

## Key engineering features

- Signed Binance API requests with bounded HTTP timeouts
- Pagination for Spot, Convert, P2P, capital, and transfer endpoints
- Non-overlapping time windows for endpoints with date-range limits
- Duplicate protection using stable Binance record identifiers
- Unique raw filenames that preserve previous ingestion runs
- Optional S3 upload using the same path structure as local storage
- Explicit Spark schemas for predictable Bronze tables
- Unity Catalog-compatible source-file metadata
- Offline unit tests with mocked API and S3 clients

## Repository structure

```text
clients/        Binance API and HTTP clients
config/         Environment-based project settings
ingestion/      End-to-end Binance ingestion workflow
storage/        Local JSON and Amazon S3 storage adapters
utils/          Request signing and history-window helpers
databricks/     Databricks notebooks for lakehouse processing
tests/          Offline unit tests
scripts/        Optional manual inspection utilities
run_ingestion.py
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add the required values to `.env`:

| Variable | Required | Description |
|---|---|---|
| `BINANCE_API_KEY` | Yes | Read-only Binance API key |
| `BINANCE_SECRET_KEY` | Yes | Binance signing secret |
| `AWS_S3_BUCKET` | For S3 upload | Destination bucket name |
| `AWS_REGION` | No | AWS region; defaults to `ap-south-1` |
| `AWS_ACCESS_KEY_ID` | No | Optional when an AWS profile or IAM role is available |
| `AWS_SECRET_ACCESS_KEY` | No | Optional when an AWS profile or IAM role is available |

Use a read-only Binance API key with IP restrictions. Withdrawal permission is
not required.

## Run the ingestion pipeline

Test locally without uploading to AWS:

```powershell
python run_ingestion.py --local-only
```

Write locally and upload the same files to S3:

```powershell
python run_ingestion.py
```

Raw files use a flat dataset layout that is compatible with the Databricks
Bronze readers:

```text
data/raw/binance/account/
data/raw/binance/trades/<SYMBOL>/
data/raw/binance/convert_trades/
data/raw/binance/p2p_buy/
data/raw/binance/p2p_sell/
data/raw/binance/deposits/
data/raw/binance/withdrawals/
data/raw/binance/transfers/<TRANSFER_TYPE>/
data/raw/binance/price_history/<SYMBOL>/
data/raw/binance/ingestion_manifest/
```

## Databricks processing

The Bronze notebook is located at:

```text
databricks/binance_data_processing/01_binance_bronze.ipynb
```

It reads the S3 raw zone and creates eight Delta tables in
`crypto_lakehouse.bronze`:

- `binance_spot_trades`
- `binance_convert_trades`
- `binance_p2p_trades`
- `binance_account_snapshots`
- `binance_deposits`
- `binance_withdrawals`
- `binance_transfers`
- `binance_price_history`

The ingestion manifest remains separate from financial tables because it
describes pipeline execution history rather than business transactions.

## Tests

The automated tests use mocks and do not call Binance or AWS:

```powershell
python -m unittest discover -s tests -v
```

Current test coverage includes pagination, date-window boundaries, duplicate
handling, signed requests, HTTP error safety, storage paths, and orchestration.

## Security and data handling

- `.env` is excluded from version control.
- Raw account and transaction files under `data/` are excluded.
- Notebook execution outputs are cleared before notebooks are committed.
- API errors do not include signed request URLs.
- Financial values remain exact strings in Bronze and become decimals in Silver.

## Roadmap

- Complete the Silver layer for balances, transfers, and price history
- Add Gold portfolio holdings and performance tables
- Add orchestration and data-quality monitoring
- Add additional centralized exchanges
- Add on-chain wallet ingestion, including Phantom-compatible Solana addresses
