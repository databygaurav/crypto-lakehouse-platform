"""Read-only client for Phantom wallet addresses."""

import json

from clients.http_client import HTTPClient

from config.settings import (
    ANKR_API_KEY,
    HELIUS_API_KEY,
    PHANTOM_SOLANA_ADDRESS,
    PHANTOM_ETHEREUM_ADDRESS,
    PHANTOM_BITCOIN_ADDRESS,
    PHANTOM_SUI_ADDRESS,
)


class PhantomClient:

    HELIUS_URL = "https://mainnet.helius-rpc.com"
    ANKR_URL = "https://rpc.ankr.com"

    def __init__(self):

        self.helius_api_key = HELIUS_API_KEY
        self.ankr_api_key = ANKR_API_KEY

        self.solana_address = PHANTOM_SOLANA_ADDRESS
        self.ethereum_address = PHANTOM_ETHEREUM_ADDRESS
        self.bitcoin_address = PHANTOM_BITCOIN_ADDRESS
        self.sui_address = PHANTOM_SUI_ADDRESS

    # ========================================================
    # HELIUS REQUEST
    # ========================================================

    def _helius_request(
        self,
        method,
        params
    ):
        """Send one read-only Solana request."""

        if not self.helius_api_key:
            raise ValueError(
                "Helius API key is required"
            )

        url = (
            f"{self.HELIUS_URL}"
            f"?api-key={self.helius_api_key}"
        )

        request_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        response = HTTPClient.post(
            url=url,
            data=json.dumps(request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        if response.get("error"):
            raise RuntimeError(
                f"Helius error: {response['error']}"
            )

        return response.get("result")

    # ========================================================
    # ANKR REQUEST
    # ========================================================

    def _ankr_request(
        self,
        blockchain,
        method,
        params
    ):
        """Send one read-only request through Ankr."""

        if not self.ankr_api_key:
            raise ValueError(
                "Ankr API key is required"
            )

        url = (
            f"{self.ANKR_URL}/"
            f"{blockchain}/"
            f"{self.ankr_api_key}"
        )

        request_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        response = HTTPClient.post(
            url=url,
            data=json.dumps(request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        if response.get("error"):
            raise RuntimeError(
                f"Ankr error: {response['error']}"
            )

        return response.get("result")

    # ========================================================
    # SOL BALANCE
    # ========================================================

    def get_sol_balance(self):
        """Return the current Phantom SOL balance."""

        if not self.solana_address:
            raise ValueError(
                "Phantom Solana address is required"
            )

        result = self._helius_request(
            method="getBalance",
            params=[
                self.solana_address,
                {
                    "commitment": "confirmed"
                }
            ]
        )

        lamports = result["value"]

        return {
            "asset": "SOL",
            "balance": (
                lamports / 1_000_000_000
            ),
            "network": "SOLANA",
            "wallet_address": self.solana_address
        }

    # ========================================================
    # ALL SOL TRANSACTIONS
    # ========================================================

    def get_all_sol_transactions(
        self,
        limit=100
    ):
        """Return complete Solana transactions for the wallet."""

        if not self.solana_address:
            raise ValueError(
                "Phantom Solana address is required"
            )

        # First, get the transaction IDs.

        signature_rows = self._helius_request(
            method="getSignaturesForAddress",
            params=[
                self.solana_address,
                {
                    "limit": limit
                }
            ]
        )

        transactions = []

        # Download the details for each transaction ID.

        for signature_row in signature_rows:

            signature = signature_row["signature"]

            transaction = self._helius_request(
                method="getTransaction",
                params=[
                    signature,
                    {
                        "encoding": "jsonParsed",
                        "commitment": "finalized",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            )

            if transaction is not None:

                transactions.append({
                    "signature": signature,
                    "transaction": transaction
                })

        return transactions

    # ========================================================
    # ETH BALANCE
    # ========================================================

    def get_eth_balance(
        self,
        wallet_address=None
    ):
        """Return the ETH balance for a public address."""

        address = (
            wallet_address
            or self.ethereum_address
        )

        if not address:
            raise ValueError(
                "Ethereum wallet address is required"
            )

        result = self._ankr_request(
            blockchain="eth",
            method="eth_getBalance",
            params=[
                address,
                "latest"
            ]
        )

        wei_balance = int(
            result,
            16
        )

        eth_balance = (
            wei_balance
            / 1_000_000_000_000_000_000
        )

        return {
            "asset": "ETH",
            "balance": eth_balance,
            "network": "ETHEREUM",
            "wallet_address": address
        }

    # ========================================================
    # ETH TRANSACTIONS
    # ========================================================

    def get_eth_transactions(
        self,
        wallet_address=None,
        limit=20
    ):
        """Return Ethereum transactions for a public address."""

        address = (
            wallet_address
            or self.ethereum_address
        )

        if not address:
            raise ValueError(
                "Ethereum wallet address is required"
            )

        result = self._ankr_request(
            blockchain="multichain",
            method="ankr_getTransactionsByAddress",
            params={
                "address": address,
                "blockchain": [
                    "eth"
                ],
                "pageSize": limit,
                "descOrder": True
            }
        )

        return result.get(
            "transactions",
            []
        )

    # ========================================================
    # ETH TOKEN BALANCES
    # ========================================================

    def get_eth_token_balances(
        self,
        wallet_address=None
    ):
        """Return tracked ERC-20 balances for an Ethereum address."""

        address = (
            wallet_address
            or self.ethereum_address
        )

        if not address:
            raise ValueError(
                "Ethereum wallet address is required"
            )

        result = self._ankr_request(
            blockchain="multichain",
            method="ankr_getAccountBalance",
            params={
                "walletAddress": address,
                "blockchain": [
                    "eth"
                ],
                "onlyWhitelisted": True
            }
        )

        tracked_symbols = {
            "LINK",
            "ONDO"
        }

        tracked_balances = []

        for asset in result.get(
            "assets",
            []
        ):

            symbol = asset.get(
                "tokenSymbol"
            )

            if symbol in tracked_symbols:

                tracked_balances.append(
                    asset
                )

        return tracked_balances

    # ========================================================
    # ETH TOKEN TRANSFERS
    # ========================================================

    def get_eth_token_transfers(
        self,
        wallet_address=None,
        limit=20
    ):
        """Return ERC-20 token transfers for an Ethereum address."""

        address = (
            wallet_address
            or self.ethereum_address
        )

        if not address:
            raise ValueError(
                "Ethereum wallet address is required"
            )

        result = self._ankr_request(
            blockchain="multichain",
            method="ankr_getTokenTransfers",
            params={
                "address": [
                    address
                ],
                "blockchain": [
                    "eth"
                ],
                "pageSize": limit,
                "descOrder": True
            }
        )

        return result.get(
            "transfers",
            []
        )

    # ========================================================
    # SUI BALANCE
    # ========================================================

    def get_sui_balance(
        self,
        wallet_address=None
    ):
        """Return the native SUI balance for a public address."""

        address = (
            wallet_address
            or self.sui_address
        )

        if not address:
            raise ValueError(
                "Sui wallet address is required"
            )

        query = f"""
        {{
            address(
                address: "{address}"
            ) {{
                balance(
                    coinType: "0x2::sui::SUI"
                ){{
                    totalBalance
                }}
            }}
        }}
        """

        response = HTTPClient.post(
            url=(
                "https://graphql.mainnet.sui.io/"
                "graphql"
            ),
            data=json.dumps({
                "query": query
            }),
            headers={
                "Content-Type": "application/json"
            },
            timeout=(15, 60)
        )

        if response.get("errors"):
            raise RuntimeError(
                f"Sui GraphQL error: "
                f"{response['errors']}"
            )

        total_balance = (
            response["data"]
            ["address"]
            ["balance"]
            ["totalBalance"]
        )

        mist_balance = int(
            total_balance
        )

        sui_balance = (
            mist_balance
            / 1_000_000_000
        )

        return {
            "asset": "SUI",
            "balance": sui_balance,
            "network": "SUI",
            "wallet_address": address
        }

    # ========================================================
    # SUI TRANSACTION HISTORY
    # ========================================================

    def get_sui_transactions(
        self,
        wallet_address=None,
        limit=10
    ):
        """Return raw transactions involving a Sui address."""

        address = (
            wallet_address
            or self.sui_address
        )

        if not address:
            raise ValueError(
                "Sui wallet address is required"
            )

        query = """
        query WalletTransactions(
            $address: SuiAddress!
            $limit: Int!
        ) {
            address(
                address: $address
            ) {
                transactions(
                    last: $limit
                    relation: AFFECTED
                ) {
                    nodes {
                        digest
                    }
                }
            }
        }
        """

        variables = {
            "address": address,
            "limit": limit
        }

        response = HTTPClient.post(
            url=(
                "https://graphql.mainnet.sui.io/"
                "graphql"
            ),
            data=json.dumps({
                "query": query,
                "variables": variables
            }),
            headers={
                "Content-Type": "application/json"
            },
            timeout=(15, 60)
        )

        if response.get("errors"):
            raise RuntimeError(
                f"Sui GraphQL error: "
                f"{response['errors']}"
            )

        return response

    # ========================================================
    # BITCOIN BALANCE
    # ========================================================

    def get_btc_balance(
        self,
        wallet_address=None
    ):
        """Return the BTC balance for a public Bitcoin address."""

        address = (
            wallet_address
            or self.bitcoin_address
        )

        if not address:
            raise ValueError(
                "Bitcoin wallet address is required"
            )

        response = HTTPClient.get(
            url=(
                "https://blockstream.info/api/"
                f"address/{address}"
            ),
            timeout=(15, 60)
        )

        confirmed_stats = response["chain_stats"]
        pending_stats = response["mempool_stats"]

        confirmed_satoshis = (
            confirmed_stats["funded_txo_sum"]
            - confirmed_stats["spent_txo_sum"]
        )

        pending_satoshis = (
            pending_stats["funded_txo_sum"]
            - pending_stats["spent_txo_sum"]
        )

        total_satoshis = (
            confirmed_satoshis
            + pending_satoshis
        )

        btc_balance = (
            total_satoshis
            / 100_000_000
        )

        return {
            "asset": "BTC",
            "balance": btc_balance,
            "network": "BITCOIN",
            "wallet_address": address
        }

    # ========================================================
    # BITCOIN TRANSACTION HISTORY
    # ========================================================

    def get_btc_transactions(
        self,
        wallet_address=None,
        limit=10
    ):
        """Return Bitcoin transactions for a public address."""

        address = (
            wallet_address
            or self.bitcoin_address
        )

        if not address:
            raise ValueError(
                "Bitcoin wallet address is required"
            )

        transactions = HTTPClient.get(
            url=(
                "https://blockstream.info/api/"
                f"address/{address}/txs"
            ),
            timeout=(15, 60)
        )

        return transactions[:limit]