import os
from datetime import datetime, timedelta
from pprint import pprint

from dotenv import load_dotenv

from alpaca_market_data_api import AlpacaMarketDataAPI

load_dotenv()
secret = os.getenv("ALPACA_SECRET")
key = os.getenv("ALPACA_KEY")

assert secret is not None, "ALPACA_SECRET environment variable is not set."
assert key is not None, "ALPACA_KEY environment variable is not set."

market_data = AlpacaMarketDataAPI(
    api_key=key,
    api_secret=secret,
)


def test_get_historical_auctions():
    data = market_data.get_historical_auctions(
        symbols=["AAPL"],
        limit=10,
        start=datetime.now() - timedelta(days=7),
        end=datetime.now() - timedelta(days=1),
    )

    # Nicely formatted json data printout
    pprint(data)


test_get_historical_auctions()


def test_get_historical_bars():
    pass


def test_get_latest_bars():
    pass


def test_get_condition_codes():
    pass


def test_get_exchange_codes():
    pass


def test_get_historical_quotes():
    pass


def test_get_latest_quotes():
    pass


def test_get_snapshots():
    pass


def test_get_historical_trades():
    pass


def test_get_latest_trades():
    pass


def test_get_most_active_stocks():
    pass


def test_get_top_market_movers():
    pass


def test_crypto_get_historical_bars():
    pass
