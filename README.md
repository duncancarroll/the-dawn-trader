<img src="https://vignette3.wikia.nocookie.net/narnia/images/9/91/Narniadawntreader.png/revision/latest?cb=20101128130243" width=500/>

# The Dawn Trader
An Automated Trading Bot for the [Kraken Exchange API](https://www.kraken.com/help/api)

## Rules
Every day (cron job):
- Do we have USD in our account? If so:
  - Calculate the amount we have available to buy (# days since last buy / total for the month)
  - Rule: If the price is lower than the last time we bought, execute a buy.

See: [The Dawn Treader](https://www.amazon.com/Voyage-Dawn-Treader-Chronicles-Narnia-ebook/dp/B001I45UEI) (C.S. Lewis)

## Libraries
- [Krakenex](https://github.com/veox/python3-krakenex) [Docs](https://python3-krakenex.readthedocs.io/en/latest/) [Examples](https://github.com/veox/python3-krakenex/tree/master/examples)
