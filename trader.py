#!/usr/bin/env python

from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from sentry_sdk import capture_message
import sentry_sdk
import os
import krakenex
import pprint
import calendar
import datetime
import time
import schedule
import time

BASE_CURRENCY = "USDT"
BASE_CURRENCY_Z = "USDT"
USD_PRECISION = Decimal('0.01')
SPEND_PER_RUN = 150.00                      # Max base currency to spend per run
ALWAYS_BUY_MINIMUM = True                   # Whether to buy or not when the minimum purchase amount of a coin exceeds the amount specified by your weight.  Warning: Setting to True will exceed SPEND_PER_RUN.
SLEEP_TIME = 60                             # Seconds the scheduler thread will sleep before checking if it needs to run
IS_DEBUG = True                             # For safety is set to true + must be overriden by env var in production
KEY_FILE = "kraken.key"                     # Created via env vars if not exist.  Warning: This is currently stored in the filesystem!
SENTRY_URL = os.environ.get("SENTRY_URL")   # Replace with your own Sentry API endpoint
sentry_sdk.init(SENTRY_URL, traces_sample_rate=1.0)

# Which currencies to purchase and a weight per coin (not percent; does not need to sum to 1)
ASSETS_AND_WEIGHTS = {
    "ETH": 1,          # ETH
    "XBT": 0.5,          # BTC
    "LINK": 0.4,          # Chainlink
    "ADA": 0.3,         # Cardano
    "DOT": 0.3,         # Polkadot
    "MATIC": 0.3,       # Polygon (Matic)
    #"XDG": 0.0,         # Doge
    #"UNI": 0.0,         # Uniswap
    #"XTZ": 0.0,           # Tezos
    #"XLTC": 0.2,        # Litecoin
    # "XXLM": 0.1,        # Lumen
    # "TRX": 0.1,         # Tron
    # "EOS": 0.1,         # EOS
    # "ALGO": 0.1,        # Algorand
    # "GRT": 0.1,         # The Graph
    # "BAT": 0.1,         # Basic Attention Token
    # "MANA": 0.1,        # Decentraland (MANA)
    # "ICX": 0.1,         # Icon
    # "SC": 0.1           # Siacoin
}

# Optional local wallets to move money into at the end of each month, so as not to keep on the Exchange.
LOCAL_WALLET_IDS = {
    "XXBT": "XXBT - Guarda Wallet",
    "XETH": "ETH - Guarda Wallet",
    "XTZ": "XTZ - Guarda Wallet",
    "XLTC": "XLTC - Guarda Wallet",
    "XXDG": "XDG - Guarda Wallet",
    "ADA": "Cardano - Guarda Wallet",
    "DOT": "DOT Guarda Wallet",
    "UNI": "UNI - Guarda Wallet",
    "LINK": "LINK Guarda Wallet"
}

def checkBalance(k):
    balance = k.query_private('Balance')['result']
    print("BALANCE (ALL):")
    pprint.pprint(balance)
    base_balance = float(balance[BASE_CURRENCY_Z])
    print("BASE BALANCE: " + str(base_balance) + " " + BASE_CURRENCY_Z)
    return base_balance
    

def getTradeableCurrencies(k):
    output = {}
    pairs = k.query_public('AssetPairs')['result']
    for tobuy in ASSETS_AND_WEIGHTS:
        for pair in pairs:
            if pair.startswith(tobuy) and pair.endswith(BASE_CURRENCY):
                output[pair] = pairs[pair]

    #pprint.pprint(pairs)
    print(str(len(output.keys()))+ " TRADEABLE PAIRS")
    return output

# Math for calculating weights
def distributeWeights(total, weights):
    scale = float(sum(weights)) / total
    return [x / scale for x in weights]

def logError(errorString):
    print(errorString)
    capture_message(errorString)

def buy():
    print("Buying coins from Kraken...")
    k = krakenex.API()
    k.load_key(KEY_FILE)
    
    # Print assets (debug)
    #assets = k.query_public('Assets')['result']
    #pprint.pprint(assets)

    base_balance = checkBalance(k)
    # If no balance in base currency, then quit
    if base_balance <= 0:
        logError("No balance, not purchasing.")
        if not IS_DEBUG:
            return

    spend_balance = SPEND_PER_RUN

    tradeable_pairs = getTradeableCurrencies(k)
    weighted_values = distributeWeights(spend_balance, ASSETS_AND_WEIGHTS.values())
    min_quantity_sum = Decimal(0)
    total_spent = Decimal('0.00')
    pprint.pprint(weighted_values)
    # Buy an equal share of each pair
    print("ABOUT TO EXECUTE " + str(len(tradeable_pairs.keys())) + " TRADES")

    i = 0
    for pair in tradeable_pairs:
        # Ticker gives us an idea of what price we should set
        ticker = k.query_public('Ticker', {'pair': pair})['result']
        if IS_DEBUG:
            print(pair + " min: " + tradeable_pairs[pair]['ordermin'])
            pprint.pprint(ticker)
        unit_price = float(ticker[pair]['a'][0])  # a = ask array(<price>, <whole lot volume>, <lot volume>),

        # Figure out how much crypto we can buy at the selected unit_price, taking care to round appropriately
        decimal_precision = tradeable_pairs[pair]['lot_decimals']    # Each currency has it's own associated decimal precision
        order_min = Decimal(tradeable_pairs[pair]['ordermin'])
        weighted_usd = Decimal(weighted_values[i]).quantize(USD_PRECISION, rounding=ROUND_DOWN)
        unit_price = Decimal(unit_price).quantize(Decimal(10) ** -decimal_precision, rounding=ROUND_DOWN)  # From https://docs.python.org/3.6/library/decimal.html#decimal-faq
        quantity = Decimal(weighted_usd / unit_price).quantize(Decimal(10) ** -decimal_precision, rounding=ROUND_DOWN)
        min_quantity_sum += order_min * unit_price
        i += 1
        
        # Don't execute the trade if it is less than the order minimum    
        if (quantity < order_min):
            if ALWAYS_BUY_MINIMUM:
                quantity = order_min
                print("*** FORCE-BUYING MINIMUM ***")
            else:
                print("Order volume of " + str(quantity) + " " + pair + " was less than order min (" + str(order_min) + "), not posting order. (Min would cost $ " + str(order_min * unit_price) + ")\n")
                continue
        else:
            print("Buying $" + str((quantity * unit_price) - (order_min * unit_price)) + " over min ($" + str(order_min * unit_price) + ")")
        
        # Execute the trade
        print("Buying " + str(quantity) + " " + tradeable_pairs[pair]['base'] + " for $" + str(unit_price * quantity) + " (unit price: " + str(unit_price) + ")\n")
        if IS_DEBUG:
            total_spent += (quantity * unit_price)
            continue
        order = k.query_private('AddOrder', {'pair':pair, 'type':'buy', 'ordertype':'market', 'volume':quantity, 'expiretm': '+80000'})
        pprint.pprint(order)
        if order['error']:
            logError("Error buying " + pair + ":" + str(order['error']))
        else:
            total_spent += (quantity * unit_price)
            print("Success!")
        print("\n")

    #print("To buy the minimum quantity of each pair costs a total of $" + str(min_quantity_sum) + " " + BASE_CURRENCY)
    print("Total spent $" + str(total_spent))
    print("Done.")


# Move coins out of Kraken periodically
def transfer():
    print("Transferring coins into local wallet...")
    
    k = krakenex.API()
    k.load_key(KEY_FILE)

    # Get up-to-date balances
    balance = k.query_private('Balance')['result']
    print("BALANCE (ALL):")
    pprint.pprint(balance)

    for asset, key in LOCAL_WALLET_IDS.items():
        if balance.get(asset) is not None:
            print(asset)
            # Print withdrawal info
            info = k.query_private('WithdrawInfo', {'asset': asset, 'key': key, 'amount': float(balance[asset])})
            if info['error']:
                logError(info['error'])
            else:
                if IS_DEBUG:
                    pprint.pprint(info)
                # Now attempt withdrawal
                print("ABOUT TO WITHDRAW " + str(float(balance[asset])) + " of: " + info['result']['method'] + " --> " + key)
                withdraw = k.query_private('Withdraw', {'asset': asset, 'key': key, 'amount': float(balance[asset])})
                if withdraw['error']:
                    logError(withdraw['error'])
                else:
                    print("Success!  Withdrew " + str(float(balance[asset])) + " of: " + info['result']['method'] + " --> " + key)
                    if IS_DEBUG:
                        pprint.pprint(withdraw)
                


# Create keyfile from env vars if not already done
if not os.path.isfile(KEY_FILE):
    Path(KEY_FILE).touch()
    with open(KEY_FILE, 'w') as f:
        f.write(os.environ.get('KRAKEN_KEY') + "\n")
        f.write(os.environ.get('KRAKEN_SECRET'))

# Check if we are a debug build
if "IS_DEBUG" in os.environ:
    if "False" in os.environ.get('IS_DEBUG'):
        IS_DEBUG = False
    print("IS_DEBUG = " + str(IS_DEBUG))

# Schedule the job if we are on production, otherwise run it immediately (but don't actually execute trades)
if not IS_DEBUG:
    schedule.every().monday.at("05:00").do(buy)         # Buy crypto
    schedule.every(4).weeks.do(transfer)    # Transfer to local wallet once a month
    print("Waiting for next execution...")
    while True:
        schedule.run_pending()
        time.sleep(SLEEP_TIME)    # Sleep for a minute
else:
    # transfer()
    buy()
    pass
