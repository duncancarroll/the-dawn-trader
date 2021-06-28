<img src="https://vignette3.wikia.nocookie.net/narnia/images/9/91/Narniadawntreader.png/revision/latest?cb=20101128130243" width=500/>

# The Dawn Trader
An automated weekly trading script for the [Kraken Exchange API](https://www.kraken.com/help/api) which spends a fixed dollar amount each week on a basket of weighted coins.  Also transfers all coins into a local wallet of your choice every month, so as not to keep them on the exchange.

## Configure
- Set weights and weekly spend amount according to preference in `ASSETS_AND_WEIGHTS` and `SPEND_PER_RUN`
- Set `LOCAL_WALLET_IDS` to empty if you don't want it to transfer your coins out every month, or enter the correct ticker symbols and Kraken string names of your wallets that you want to transfer each coin into (must be created as standard outbound wallets in Kraken web UI first.)
- Create a Kraken API key with permission to buy coins and add `KRAKEN_KEY` and `KRAKEN_SECRET` to env vars.
- `$ ./venv/bin/activate`
- `$ pip install -r requirements.txt`
- `$ python trader.py`

## Deploy
- Ensure env var `IS_DEBUG` to False in cloud
- Remove my Sentry API key (whoops)
- Digital Ocean has a nice 1-click app deploy via commit hook which works great for this.
- Note: This script does not use cron, instead runs as a periodically looping thread w/Python scheduler to keep things simple.
- Also note: `unit_price` is set to buy at market ask, but this can be modified if you're feeling lucky.

See: [The Dawn Treader](https://www.amazon.com/Voyage-Dawn-Treader-Chronicles-Narnia-ebook/dp/B001I45UEI) (C.S. Lewis)

## Libraries
- [Krakenex](https://github.com/veox/python3-krakenex) [Docs](https://python3-krakenex.readthedocs.io/en/latest/) [Examples](https://github.com/veox/python3-krakenex/tree/master/examples)
