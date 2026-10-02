from ingestion.mudrex_ingestion import (
    get_deposits,
    get_inr_spot_trades,
    get_usdt_spot_trades,
    get_withdrawals,
    get_earn_history,
    get_usdt_fund_transactions
)


usdt_trades = get_usdt_spot_trades()
inr_trades = get_inr_spot_trades()
deposits = get_deposits()
withdrawals = get_withdrawals()
earn_history = get_earn_history()
usdt_fund_transactions = get_usdt_fund_transactions()


print(
    "USDT Spot trade rows:",
    len(usdt_trades)
)

print(
    "INR Spot trade rows:",
    len(inr_trades)
)

print(
    "Deposit rows:",
    len(deposits)
)

print(
    "Withdrawal rows:",
    len(withdrawals)
)

print(withdrawals)

print(
    "Earn history rows:",
    len(earn_history)
)

print(earn_history[:3])

print(
    "USDT fund transaction rows:",
    len(usdt_fund_transactions)
)