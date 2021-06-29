<img src="https://vignette3.wikia.nocookie.net/narnia/images/9/91/Narniadawntreader.png/revision/latest?cb=20101128130243" width=500/>

# The Dawn Trader
I got tired of forgetting to buy crypto so I wrote this script to buy a fixed USD amount once a week from a weighted list of specified coins.  The only thing you have to do manually is get USD into your Kraken account somehow, usually wire (ideally your bank offers recurring wire transfers.)  The script will also transfer all coins into a specified wallet of your choice every month, so as not to keep them on the exchange.  Uses the [Kraken Exchange API](https://www.kraken.com/help/api)

See: [The Dawn Treader](https://www.amazon.com/Voyage-Dawn-Treader-Chronicles-Narnia-ebook/dp/B001I45UEI) (C.S. Lewis)


## Configure
- Add the coins you want to buy plus weights into `ASSETS_AND_WEIGHTS` and the weekly spend amount into `SPEND_PER_RUN`
- Set `ALWAYS_BUY_MINIMUM` to False if you don't want to overspend, or leave at True if you still want to buy even when the minimum amount exceeds the weight you set.
- Set `LOCAL_WALLET_IDS` to empty if you don't want it to transfer your coins out every month, or enter the correct ticker symbols and Kraken string names of your wallets that you want to transfer each coin into (must be created as standard outbound wallets in Kraken web UI first.)
- Create a Kraken API key with permission to buy coins and add `KRAKEN_KEY` and `KRAKEN_SECRET` to env vars.
- `$ virtualenv venv`
- `$ ./venv/bin/activate`
- `$ pip install -r requirements.txt`
- `$ python trader.py`

## Deploy
- Can be deployed to anything that runs Python.  Does not need cron b/c we tie up a thread lol
- Ensure env var `IS_DEBUG` to False in cloud
- Remove my Sentry API key (whoops)
- Digital Ocean has a nice 1-click app deploy via commit hook which works great for this.
- Also note: `unit_price` is set to buy at market ask, but this can be modified if you're feeling lucky.

## Libraries
- [Krakenex](https://github.com/veox/python3-krakenex) [Docs](https://python3-krakenex.readthedocs.io/en/latest/) [Examples](https://github.com/veox/python3-krakenex/tree/master/examples)
