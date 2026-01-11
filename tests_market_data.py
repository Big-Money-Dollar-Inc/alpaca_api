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


def test_get_historical_auctions() -> None:
    data = market_data.get_historical_auctions(
        symbols=["AAPL"],
        limit=10,
        start=datetime.now() - timedelta(days=7),
        end=datetime.now() - timedelta(days=1),
    )

    # Nicely formatted json data printout
    pprint(data)


# test_get_historical_auctions()


def test_get_historical_bars() -> None:
    data = market_data.get_historical_bars(
        symbols=["AAPL"],
        limit=10,
        start=datetime.now() - timedelta(days=7),
        end=datetime.now() - timedelta(days=1),
    )

    # Nicely formatted json data printout
    pprint(data)


# test_get_historical_bars()


def test_get_latest_bars() -> None:
    data = market_data.get_latest_bars(
        symbols=["AAPL"],
    )

    # Nicely formatted json data printout
    pprint(data)


# test_get_latest_bars()


def test_get_condition_codes() -> None:
    data = market_data.get_condition_codes()

    # Nicely formatted json data printout
    pprint(data)


# test_get_condition_codes()


def test_get_exchange_codes() -> None:
    data = market_data.get_exchange_codes()

    # Nicely formatted json data printout
    pprint(data)


# test_get_exchange_codes()


def test_get_historical_quotes() -> None:
    data = market_data.get_historical_quotes(
        symbols=["AAPL"],
        limit=10,
        start=datetime.now() - timedelta(days=7),
        end=datetime.now() - timedelta(days=1),
    )

    # Nicely formatted json data printout
    pprint(data)


# test_get_historical_quotes()


def test_get_latest_quotes() -> None:
    data = market_data.get_latest_quotes(symbols=["AAPL"])

    # Nicely formatted json data printout
    pprint(data)


# test_get_latest_quotes()


def test_get_snapshots() -> None:
    data = market_data.get_snapshots(symbols=["AAPL"])

    # Nicely formatted json data printout
    pprint(data)


# test_get_snapshots()


def test_get_historical_trades() -> None:
    data = market_data.get_historical_trades(
        symbols=["AAPL"],
        limit=10,
        start=datetime.now() - timedelta(days=7),
        end=datetime.now() - timedelta(days=1),
    )

    # Nicely formatted json data printout
    pprint(data)


# test_get_historical_trades()


def test_get_latest_trades() -> None:
    data = market_data.get_latest_trades(symbols=["AAPL"])

    # Nicely formatted json data printout
    pprint(data)


# test_get_latest_trades()


def test_get_most_active_stocks() -> None:
    data = market_data.get_most_active_stocks()

    # Nicely formatted json data printout
    pprint(data)


# test_get_most_active_stocks()


def test_get_top_market_movers() -> None:
    data = market_data.get_top_market_movers()

    # Nicely formatted json data printout
    pprint(data)


# test_get_top_market_movers()


def test_crypto_get_historical_bars() -> None:
    data = market_data.crypto_get_historical_bars(loc="us", symbols=["BTC/USD"], timeframe="1Min")

    # Nicely formatted json data printout
    pprint(data)


# test_crypto_get_historical_bars()
