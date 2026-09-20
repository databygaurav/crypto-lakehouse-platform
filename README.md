# Crypto Lakehouse Platform

A portfolio data-engineering project that collects Binance and Giottus account,
trade, funding, and market history; stores immutable JSON files locally and in
Amazon S3; and processes the data in Databricks using a medallion architecture.

```text
Exchange APIs
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
| Python ingestion | Complete | Downloads Binance and Giottus data and stores raw JSON |
| Local and S3 storage | Complete | Preserves source responses in dataset-specific folders |
| Databricks Bronze | Complete | Applies explicit schemas, lineage metadata, and record-level deduplication |
| Databricks Silver | Complete | Standardizes types and combines related transaction sources |
| Gold analytics | Complete | Provides shared dimensions, movements, balances, prices, and portfolio facts |

## Data collected

- Binance Spot account snapshots and balances
- Binance Funding wallet snapshots and balances
- Binance and Giottus Spot trade history for configured trading pairs
- Giottus EBES trades and INR account balances
- Binance Convert transactions
- P2P BUY and SELL orders
- Crypto and fiat deposits and withdrawals
- Universal account transfers
- Daily candlestick price history
- An ingestion manifest for each completed run

## Key engineering features

- Signed Binance and Giottus API requests with bounded HTTP timeouts
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
clients/        Binance, Giottus, and shared HTTP clients
config/         Environment-based project settings
ingestion/      Exchange-specific ingestion workflows
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
| `GIOTTUS_API_KEY` | For Giottus | Read-only Giottus API key |
| `GIOTTUS_SECRET_KEY` | For Giottus | Giottus signing secret |
| `AWS_S3_BUCKET` | For S3 upload | Destination bucket name |
| `AWS_REGION` | No | AWS region; defaults to `ap-south-1` |
| `AWS_ACCESS_KEY_ID` | No | Optional when an AWS profile or IAM role is available |
| `AWS_SECRET_ACCESS_KEY` | No | Optional when an AWS profile or IAM role is available |

Use read-only exchange API keys with IP restrictions. Withdrawal permission is
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

Run Giottus ingestion locally:

```powershell
python -m ingestion.giottus_ingestion --local-only
```

Run Giottus ingestion locally and upload to S3:

```powershell
python -m ingestion.giottus_ingestion
```

Raw files use a flat dataset layout that is compatible with the Databricks
Bronze readers:

```text
data/raw/binance/account/
data/raw/binance/funding_account/
data/raw/binance/trades/<SYMBOL>/
data/raw/binance/convert_trades/
data/raw/binance/p2p_buy/
data/raw/binance/p2p_sell/
data/raw/binance/deposits/
data/raw/binance/withdrawals/
data/raw/binance/transfers/<TRANSFER_TYPE>/
data/raw/binance/price_history/<SYMBOL>/
data/raw/binance/ingestion_manifest/
data/raw/giottus/balances/
data/raw/giottus/trades/<SYMBOL>/
data/raw/giottus/ebes_trades/<SYMBOL>/
data/raw/giottus/crypto_deposits/
data/raw/giottus/crypto_withdrawals/
data/raw/giottus/fiat_deposits/
data/raw/giottus/fiat_withdrawals/
data/raw/giottus/ingestion_manifest/
```

## Databricks processing

Notebooks are organized by medallion layer:

```text
databricks/
├── 01_bronze/
│   ├── 01_binance_bronze.ipynb
│   └── 02_giottus_bronze.ipynb
├── 02_silver/
│   ├── 01_binance_silver.ipynb
│   └── 02_giottus_silver.ipynb
└── 03_gold/
    ├── dimensions_gold.ipynb
    └── fact_gold.ipynb
```

Bronze preserves raw exchange records with source-file metadata. Silver applies
business names and exact decimal types. Gold combines both exchanges into shared
dimensions and facts for trades, asset movements, balance snapshots, daily
balances, daily prices, and portfolio valuation.

The ingestion manifest remains separate from financial tables because it
describes pipeline execution history rather than business transactions.

## Tests

The automated tests use mocks and do not call exchange APIs or AWS:

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

- Add historical INR/USDT rates for dual-currency portfolio valuation
- Add orchestration and data-quality monitoring
- Add CoinDCX, Mudrex, and other centralized exchanges
- Add on-chain wallet ingestion, including Phantom-compatible Solana addresses
