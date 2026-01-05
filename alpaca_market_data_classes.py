from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict


@dataclass
class Bar:
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    number_of_trades: int
    volume_weighted_average_price: float


@dataclass
class Auction:
    datetime: datetime
    exchange_code: str
    auction_price: float
    auction_trade_size: int
    condition_flag: str


class AuctionsDict(TypedDict):
    opening_auctions: list[Auction]
    closing_auctions: list[Auction]


@dataclass
class HistoricalAuctions:
    datetime: datetime | None = None
    auctions: dict[str, AuctionsDict] | None = None
    currency: str | None = None
    next_page_token: str | None = None


# Latest Auction response class
@dataclass
class HistoricalBars:
    bars: dict[str, list[Bar]]
    currency: str
    next_page_token: str | None


# Latest Bars response class
@dataclass
class LatestBars:
    bars: dict[str, list[Bar]]
    currency: str


# Condition Codes class
@dataclass
class ConditionCodes:
    codes: dict[str, str]


# Exchange Codes class
@dataclass
class ExchangeCodes:
    codes: dict[str, str]


# Quote class
@dataclass
class Quote:
    datetime: datetime
    bid_exchange: str
    bid_price: float
    bid_size: int
    ask_exchange: str
    ask_price: float
    ask_size: int
    condition_codes: list[str]


# Historical Quotes response class
@dataclass
class HistoricalQuotes:
    quotes: dict[str, list[Quote]]
    currency: str
    next_page_token: str | None


# Latest Quotes response class
@dataclass
class LatestQuotes:
    quotes: dict[str, list[Quote]]
    currency: str


@dataclass
class Trade:
    datetime: datetime
    exchange: str
    price: float
    size: int
    trade_id: int
    condition_codes: list[str]
    timezone: str
    trade_update: str


@dataclass
class Snapshot:
    daily_bar: Bar
    latest_quote: Quote
    latest_trade: Trade
    minute_bar: Bar
    previous_daily_bar: Bar


@dataclass
class Snapshots:
    snapshots: dict[str, Snapshot]


@dataclass
class HistoricalTrades:
    trades: dict[str, list[Trade]]
    currency: str
    next_page_token: str | None


@dataclass
class LatestTrades:
    trades: dict[str, list[Trade]]
    currency: str


@dataclass
class MostActiveStock:
    symbol: str
    volume: int
    trade_count: int


@dataclass
class MostActiveStocks:
    most_active_stocks: dict[str, MostActiveStock]
    last_updated: datetime


@dataclass
class Mover:
    symbol: str
    percentage_change: float
    change: float
    price: float


@dataclass
class TopMarketMovers:
    gainers: dict[str, Mover]
    losers: dict[str, Mover]
    market_type: str
    last_updated: datetime
