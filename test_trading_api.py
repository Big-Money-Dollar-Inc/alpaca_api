import os
from pprint import pprint

from dotenv import load_dotenv

from alpaca_trading_api import AlpacaTradingAPI

load_dotenv()
secret = os.getenv("ALPACA_SECRET")
key = os.getenv("ALPACA_KEY")

assert secret is not None, "ALPACA_SECRET environment variable is not set."
assert key is not None, "ALPACA_KEY environment variable is not set."

market_data = AlpacaTradingAPI(api_key=key, api_secret=secret, paper=True)


def test_get_account():
    data = market_data.get_account()

    # Nicely formatted json data printout
    pprint(data)


# test_get_account()


def test_get_assets():
    data = market_data.get_assets()

    # Nicely formatted json data printout
    pprint(data)


# test_get_assets()


def test_get_asset():
    data = market_data.get_asset("AAPL")

    # Nicely formatted json data printout
    pprint(data)


# test_get_asset()


def test_create_order():
    data = market_data.create_order(symbol="AAPL", side="buy", qty=2)

    # Nicely formatted json data printout
    pprint(data)


# test_create_order()


def test_get_all_orders():
    data = market_data.get_all_orders()

    # Nicely formatted json data printout
    pprint(data)


# test_get_all_orders()


def test_delete_all_orders():
    data = market_data.delete_all_orders()

    # Nicely formatted json data printout
    pprint(data)


# test_delete_all_orders()
