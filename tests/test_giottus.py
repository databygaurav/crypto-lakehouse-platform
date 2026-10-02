import requests

from clients.giottus_client import GiottusClient


client = GiottusClient()


# ALL SPOT TRADES

try: 
    trades = client.get_all_trades(
        symbol="SOL/INR"
    )

    print("\nTotal Spot trades:", len(trades))
    print(trades)

except requests.HTTPError as error:
    print(
        "Request failed. HTTP status:",
        error.response.status_code
    )


# ALL EBES TRADES

try: 
    ebes_trades = client.get_all_ebes_trades(
        symbol="SOL/INR"
    )

    print("\nTotal EBES trades:", len(ebes_trades))
    print(ebes_trades)

except requests.HTTPError as error:
    print(
        "Request failed. HTTP status:",
        error.response.status_code
    )


# ALL CRYPTO DEPOSITS

try: 
    crypto_deposits = client.get_all_crypto_deposits(
        asset="SOL"
    )

    print("\nTotal Crypto deposits:", len(crypto_deposits))
    print(crypto_deposits)

except requests.HTTPError as error:
    print(
        "Request failed. HTTP status:",
        error.response.status_code
    )


# ALL CRYPTO WITHDRAWALS

try: 
    crypto_withdrwals = client.get_all_crypto_withdrawals(
        asset="SOL"
    )

    print("\nTotal Crypto withdrawals:", len(crypto_withdrwals))
    print(crypto_withdrwals)

except requests.HTTPError as error:
    print(
        "Request failed. HTTP status:",
        error.response.status_code
    )


# ALL FIAT DEPOSITS

try:
    fiat_deposits = client.get_all_fiat_deposits()

    print("\nTotal Fiat deposits:", len(fiat_deposits))
    print(fiat_deposits)


except requests.HTTPError as error:
    print(
        "Request failed. HTTP status:",
        error.response.status_code
    )


# ALL FIAT WITHDRAWALS

try:
    fiat_withdrawals = client.get_all_fiat_withdrawals()

    print("\nTotal Fiat withdrawals:", len(fiat_withdrawals))
    print(fiat_withdrawals)


except requests.HTTPError as error:
    print(
        "Request failed. HTTP status:",
        error.response.status_code
    )