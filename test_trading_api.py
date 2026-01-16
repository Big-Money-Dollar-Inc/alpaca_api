import os
from pprint import pprint

from dotenv import load_dotenv

from alpaca_trading_api import AlpacaTradingAPI

load_dotenv()
secret = os.getenv("ALPACA_SECRET")
key = os.getenv("ALPACA_KEY")

assert secret is not None, "ALPACA_SECRET environment variable is not set."
assert key is not None, "ALPACA_KEY environment variable is not set."

trading_api = AlpacaTradingAPI(api_key=key, api_secret=secret, paper=True)


def test_get_account() -> None:
    data = trading_api.get_account()

    # Nicely formatted json data printout
    pprint(data)


# test_get_account()


def test_get_assets() -> None:
    data = trading_api.get_assets()

    # Nicely formatted json data printout
    pprint(data)


# test_get_assets()


def test_get_asset() -> None:
    data = trading_api.get_asset("AAPL")

    # Nicely formatted json data printout
    pprint(data)


# test_get_asset()


def test_create_order() -> None:
    data = trading_api.create_order(symbol="AAPL", side="buy", qty=2)

    # Nicely formatted json data printout
    pprint(data)


# test_create_order()


def test_get_all_orders() -> None:
    data = trading_api.get_all_orders()

    # Nicely formatted json data printout
    pprint(data)


# test_get_all_orders()


def test_delete_all_orders() -> None:
    data = trading_api.delete_all_orders()

    # Nicely formatted json data printout
    pprint(data)


# test_delete_all_orders()


def test_get_order_by_client_order_id() -> None:
    data = trading_api.get_order_by_client_order_id(
        client_order_id="58486581-2099-4394-a54d-094b5dd1810d"
    )

    # Nicely formatted json data printout
    pprint(data)


# test_get_order_by_client_order_id()


def test_get_order_by_id() -> None:
    data = trading_api.get_order_by_id(order_id="d314af94-7b2e-42be-85dd-aa6978c055ae")

    # Nicely formatted json data printout
    pprint(data)


# test_get_order_by_id()


# TODO: Tricky need to come back to this.
def test_replace_order_by_id() -> None:
    data = trading_api.replace_order_by_id(order_id="f3e0b69f-b84d-459d-b8e5-6895b62f3954", qty=3)

    # Nicely formatted json data printout
    pprint(data)


# test_replace_order_by_id()


def test_cancel_order_by_id() -> None:
    data = trading_api.cancel_order_by_id(order_id="b28fc094-e033-4490-98d1-350eb276638b")

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
