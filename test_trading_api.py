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
    data = market_data.create_order(symbol="AAPL", side="buy", qty=2, client_order_id="test")

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


def test_get_order_by_client_order_id():
    data = market_data.get_order_by_client_order_id(client_order_id="test")

    # Nicely formatted json data printout
    pprint(data)


# test_get_order_by_client_order_id()


def test_get_order_by_id():
    data = market_data.get_order_by_id(order_id="d314af94-7b2e-42be-85dd-aa6978c055ae")

    # Nicely formatted json data printout
    pprint(data)


# test_get_order_by_id()


# TODO: Tricky need to come back to this.
def test_replace_order_by_id():
    data = market_data.replace_order_by_id(order_id="23ede4f6-e6c7-49ee-bac7-c7846a73678e", qty=3)

    # Nicely formatted json data printout
    pprint(data)


# test_replace_order_by_id()


def test_cancel_order_by_id():
    data = market_data.cancel_order_by_id(order_id="23ede4f6-e6c7-49ee-bac7-c7846a73678e")

    # Nicely formatted json data printout
    pprint(data)


test_cancel_order_by_id()
# get_all_positions
# close_all_positions
# get_open_position
# close_position
# exercise_option
# get_account_portfolio_history
# get_market_clock
