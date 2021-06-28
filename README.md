<img src="https://vignette3.wikia.nocookie.net/narnia/images/9/91/Narniadawntreader.png/revision/latest?cb=20101128130243" width=500/>

# The Dawn Trader
An automated weekly trading script for the [Kraken Exchange API](https://www.kraken.com/help/api) which spends a fixed dollar amount each week on a basket of weighted coins.

## Configure
- Set weights and weekly spend amount according to preference.
- `$ ./venv/bin/activate`
- `$ pip install -r requirements.txt`

## Deploy
- Add your Kraken API key, etc as environment variables, ensure it has proper permissions.
- Remove my Sentry API key (whoops)
- Digital Ocean has a nice 1-click app deploy via commit hook which works great.
- Note: Script runs as a looping thread w/Python scheduler to keep things simple.

See: [The Dawn Treader](https://www.amazon.com/Voyage-Dawn-Treader-Chronicles-Narnia-ebook/dp/B001I45UEI) (C.S. Lewis)

## Libraries
- [Krakenex](https://github.com/veox/python3-krakenex) [Docs](https://python3-krakenex.readthedocs.io/en/latest/) [Examples](https://github.com/veox/python3-krakenex/tree/master/examples)
