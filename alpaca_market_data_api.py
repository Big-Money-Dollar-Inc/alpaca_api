from collections.abc import Mapping, Sequence
from datetime import datetime
from pprint import pprint
from typing import Any, cast

from requests import Session

from alpaca_api_request_handler import (
    InvalidAlpacaPayloadError,
    InvalidLimitParameterError,
    InvalidSortParameterError,
    JsonResponseError,
    RequestOptions,
    alpaca_api_request,
)
from alpaca_market_data_classes import (
    Auction,
    Bar,
    ConditionCodes,
    ExchangeCodes,
    HistoricalAuctions,
    HistoricalBars,
    HistoricalQuotes,
    HistoricalTrades,
    LatestBars,
    LatestQuotes,
    MostActiveStock,
    MostActiveStocks,
    Mover,
    Quote,
    Snapshot,
    Snapshots,
    TopMarketMovers,
    Trade,
)

OK_RESPONSE_CODE = 200
CRYPTO_MIN_DATA_POINTS = 1
CRYPTO_MAX_DATA_POINTS = 10000


class AlpacaMarketDataAPI:
    """
    Alpaca REST Client for accessing Alpaca's market data API.
    """

    def __init__(
        self, api_key: str, api_secret: str, request_session: Session | None = None
    ) -> None:
        """
        :param api_key: Your Alpaca API key ID.
        :param api_secret: Your Alpaca API secret.
        :param paper: If True, use paper trading endpoints.
        """
        self.base_url = "https://data.alpaca.markets"
        # Note: The base URL for market data is always the same, regardless of paper trading
        if request_session:
            self.session = request_session
        else:
            self.session = Session()
        self.session.headers.update(self._headers(api_key, api_secret))

    @staticmethod
    def _headers(api_key: str, api_secret: str) -> dict[str, str]:
        return {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": api_secret,
            "Content-Type": "application/json",
        }

    def _parse_ts(self, value: str) -> datetime:
        if not isinstance(value, str):
            raise InvalidAlpacaPayloadError
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _req_str(self, d: dict[str, Any], key: str) -> str:
        v = d.get(key)
        if not isinstance(v, str):
            raise InvalidAlpacaPayloadError
        return v

    def _req_float(self, d: dict[str, Any], key: str) -> float:
        v = d.get(key)
        if isinstance(v, (int, float)):
            return float(v)
        raise InvalidAlpacaPayloadError

    def _req_int(self, d: dict[str, Any], key: str) -> int:
        v = d.get(key)
        print(v)
        if isinstance(v, int):
            return v
        if isinstance(v, float) and v.is_integer():
            return int(v)
        raise InvalidAlpacaPayloadError

    def _parse_auction_list(self, raw: list[dict[str, str | float]] | None) -> list[Auction]:
        if not raw:
            return []

        out: list[Auction] = []
        for a in raw:
            out.append(
                Auction(
                    datetime=self._parse_ts(self._req_str(a, "t")),
                    exchange_code=self._req_str(a, "x"),
                    auction_price=self._req_float(a, "p"),
                    auction_trade_size=self._req_int(a, "s"),
                    condition_flag=self._req_str(a, "c"),
                )
            )
        return out

    def get_historical_auctions(
        self,
        symbols: list[str | None],
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> HistoricalAuctions:
        params = {
            "symbols": symbols,
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ") if start else None,
            "end": end.strftime("%Y-%m-%dT%H:%M:%SZ") if end else None,
            "limit": limit,
        }

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/auctions",
            options=RequestOptions(params=params),
        )

        try:
            auctions_by_symbol: dict[str, Any] = (
                data["auctions"] if isinstance(data["auctions"], dict) else {}
            )

            parsed: dict[str, Any] = {}

            for symbol, list in auctions_by_symbol.items():
                parsed_days = []
                for day_obj in list:
                    parsed_days.append(
                        {
                            "date": self._req_str(day_obj, "d"),
                            "opening_auctions": self._parse_auction_list(day_obj.get("o")),
                            "closing_auctions": self._parse_auction_list(day_obj.get("c")),
                        }
                    )

                parsed[symbol] = parsed_days

            print(data)

            return HistoricalAuctions(
                auctions=parsed,
            )

        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def _parse_bars_list(self, raw: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        if not raw:
            return []

        out: list[dict[str, Any]] = []
        for b in raw:
            out.append(
                {
                    "timestamp": self._parse_ts(self._req_str(b, "t")),
                    "open": self._req_float(b, "o"),
                    "high": self._req_float(b, "h"),
                    "low": self._req_float(b, "l"),
                    "close": self._req_float(b, "c"),
                    "volume": self._req_int(b, "v"),
                    "number_of_trades": self._req_int(b, "n"),
                    "volume_weighted_average_price": self._req_float(b, "vw"),
                }
            )
        return out

    def get_historical_bars(
        self,
        symbols: list[str],
        timeframe: str = "1H",
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
        feed: str | None = "iex",
        page_token: str | None = None,
    ) -> HistoricalBars:
        """
        Fetch historical bar data for a given symbol.

        :param symbol: The stock symbol to fetch bars for.
        :param start: Start date in ISO format (YYYY-MM-DD).
        :param end: End date in ISO format (YYYY-MM-DD).
        :param limit: Maximum number of records to return.
        :return: JSON response containing bar data.
        """
        params: dict[str, Any] = {
            "symbols": symbols,
            "timeframe": timeframe,
            "limit": limit,
            "feed": feed,
        }
        if start is not None:
            params["start"] = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end is not None:
            params["end"] = end.strftime("%Y-%m-%dT%H:%M:%SZ")
        if page_token:
            params["page_token"] = page_token

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/bars",
            options=RequestOptions(params=params),
        )

        try:
            bars_by_symbol: dict[str, Any] = data["bars"] if isinstance(data["bars"], dict) else {}

            parsed: dict[str, Any] = {}

            for symbol, list in bars_by_symbol.items():
                parsed_bars = []
                parsed_bars.append(
                    self._parse_bars_list(list),
                )

                parsed[symbol] = parsed_bars

            return HistoricalBars(
                bars=parsed,
                next_page_token=self._req_str(data, "next_page_token"),
            )

        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def get_latest_bars(self, symbols: list[str]) -> LatestBars:
        """
        Fetch the latest bar data for one or more symbols
        (always returns a dict under the "bars" key).
        """

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/bars/latest",
            options=RequestOptions(params={"symbols": symbols}),
        )
        try:
            bars_by_symbol: dict[str, Any] = data["bars"] if isinstance(data["bars"], dict) else {}

            parsed: dict[str, Any] = {}

            for symbol, list in bars_by_symbol.items():
                parsed_bars = []
                parsed_bars.append(
                    {
                        "timestamp": self._parse_ts(list.get("t")),
                        "open": self._req_float(list, "o"),
                        "high": self._req_float(list, "h"),
                        "low": self._req_float(list, "l"),
                        "close": self._req_float(list, "c"),
                        "volume": self._req_int(list, "v"),
                        "number_of_trades": self._req_int(list, "n"),
                        "volume_weighted_average_price": self._req_float(list, "vw"),
                    }
                )

                parsed[symbol] = parsed_bars

            return LatestBars(
                bars=parsed,
            )
        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def get_condition_codes(
        self, ticktype: str | None = "trade", tape: str = "A"
    ) -> ConditionCodes:
        """
        Fetch the condition codes used in market data.

        :return: JSON response containing condition codes.
        """
        params = {"tape": tape}

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path=f"/v2/stocks/meta/conditions/{ticktype}",
            options=RequestOptions(params={k: v for k, v in params.items() if v is not None}),
        )

        try:
            parsed: dict[str, str] = {}

            for code, description in data.items():
                if isinstance(description, str):
                    parsed[code] = description

            return ConditionCodes(codes=parsed)
        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def get_exchange_codes(self) -> ExchangeCodes:
        """
        Fetch the exchange codes used in market data.

        :return: JSON response containing exchange codes.
        """
        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/meta/exchanges",
        )

        try:
            parsed: dict[str, str] = {}

            for code, description in data.items():
                if isinstance(description, str):
                    parsed[code] = description

            return ExchangeCodes(codes=parsed)
        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def _parse_historical_quotes_list(
        self, raw: list[dict[str, Any]] | None
    ) -> list[dict[str, Any]]:
        if not raw:
            return []

        out: list[dict[str, Any]] = []
        for q in raw:
            out.append(
                {
                    "timestamp": self._parse_ts(self._req_str(q, "t")),
                    "bid_exchange": self._req_str(q, "bx"),
                    "bid_price": self._req_float(q, "bp"),
                    "bid_size": self._req_int(q, "bs"),
                    "ask_exchange": self._req_str(q, "ax"),
                    "ask_price": self._req_float(q, "ap"),
                    "ask_size": self._req_int(q, "as"),
                }
            )
        return out

    def get_historical_quotes(
        self,
        symbols: list[str],
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
        feed: str | None = "iex",
    ) -> HistoricalQuotes:
        """
        Fetch historical quote data for a given symbol.

        :param symbol: The stock symbol to fetch quotes for.
        :param start: Start date in ISO format (YYYY-MM-DD).
        :param end: End date in ISO format (YYYY-MM-DD).
        :param limit: Maximum number of records to return.
        :return: JSON response containing quote data.
        """
        params = {
            "symbols": ",".join(symbols),
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ") if start else None,
            "end": end.strftime("%Y-%m-%dT%H:%M:%SZ") if end else None,
            "limit": limit,
            "feed": feed,
        }

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/quotes",
            options=RequestOptions(params=params),
        )

        print(data)

        try:
            quotes_by_symbol = data.get("quotes") or {}

            parsed: dict[str, Any] = {}

            if isinstance(quotes_by_symbol, Mapping):
                for symbol, list in quotes_by_symbol.items():
                    parsed_quotes = []
                    parsed_quotes.append(
                        self._parse_historical_quotes_list(list),
                    )

                    parsed[symbol] = parsed_quotes

            return HistoricalQuotes(
                quotes=parsed,
                next_page_token=self._req_str(data, "next_page_token"),
            )
        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def get_latest_quotes(self, symbols: list[str]) -> LatestQuotes:
        """
        Fetch the latest quote data for a given symbol.

        :param symbols: The stock symbols to fetch the latest quote for.
        :return: JSON response containing the latest quote data.
        """

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/quotes/latest",
            options=RequestOptions(params={"symbols": symbols}),
        )

        try:
            quotes_by_symbol = data.get("quotes") or {}

            parsed: dict[str, Any] = {}
            if isinstance(quotes_by_symbol, Mapping):
                list = cast("Mapping[str, object]", quotes_by_symbol)
                for symbol, list in quotes_by_symbol.items():
                    parsed_quotes = []
                    parsed_quotes.append(
                        {
                            "timestamp": self._parse_ts(self._req_str(list, "t")),
                            "bid_exchange": self._req_str(list, "bx"),
                            "bid_price": self._req_float(list, "bp"),
                            "bid_size": self._req_int(list, "bs"),
                            "ask_exchange": self._req_str(list, "ax"),
                            "ask_price": self._req_float(list, "ap"),
                            "ask_size": self._req_int(list, "as"),
                        }
                    )

                    parsed[symbol] = parsed_quotes

            return LatestQuotes(quotes=parsed)
        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def _parse_bar(self, raw: dict[str, Any]) -> Bar:
        return Bar(
            datetime=self._parse_ts(self._req_str(raw, "t")),
            open=self._req_float(raw, "o"),
            high=self._req_float(raw, "h"),
            low=self._req_float(raw, "l"),
            close=self._req_float(raw, "c"),
            volume=self._req_int(raw, "v"),
            number_of_trades=self._req_int(raw, "n"),
            volume_weighted_average_price=self._req_float(raw, "vw"),
        )

    def _parse_quote(self, raw: dict[str, Any]) -> Quote:
        return Quote(
            datetime=self._parse_ts(self._req_str(raw, "t")),
            bid_exchange=self._req_str(raw, "bx"),
            bid_price=self._req_float(raw, "bp"),
            bid_size=self._req_int(raw, "bs"),
            ask_exchange=self._req_str(raw, "ax"),
            ask_price=self._req_float(raw, "ap"),
            ask_size=self._req_int(raw, "as"),
            condition_codes=raw.get("c", []),
        )

    def _parse_trade(self, raw: dict[str, Any]) -> Trade:
        return Trade(
            datetime=self._parse_ts(self._req_str(raw, "t")),
            exchange=self._req_str(raw, "x"),
            price=self._req_float(raw, "p"),
            size=self._req_int(raw, "s"),
            trade_id=self._req_int(raw, "i"),
            condition_codes=raw.get("c", []),
            timezone=self._req_str(raw, "z"),
            trade_update=self._req_str(raw, "u") if raw.get("u") else "N/A",
        )

    def get_snapshots(self, symbols: list[str]) -> Snapshots:
        """
        Fetch snapshots for one or more symbols.

        :param symbols: Comma-separated list of stock symbols.
        :return: JSON response containing snapshot data.
        """

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/snapshots",
            options=RequestOptions(params={"symbols": symbols} if symbols else {}),
        )

        print(data)

        try:
            parsed: dict[str, Any] = {}

            for symbol, snap in data.items():
                if isinstance(snap, Mapping):
                    daily_bar_obj = snap.get("dailyBar")
                    latest_quote_obj = snap.get("latestQuote")
                    latest_trade_obj = snap.get("latestTrade")
                    minute_bar_obj = snap.get("minuteBar")
                    prev_daily_bar_obj = snap.get("prevDailyBar")

                    if not isinstance(daily_bar_obj, Mapping):
                        raise InvalidAlpacaPayloadError
                    if not isinstance(latest_quote_obj, Mapping):
                        raise InvalidAlpacaPayloadError
                    if not isinstance(latest_trade_obj, Mapping):
                        raise InvalidAlpacaPayloadError
                    if not isinstance(minute_bar_obj, Mapping):
                        raise InvalidAlpacaPayloadError
                    if not isinstance(prev_daily_bar_obj, Mapping):
                        raise InvalidAlpacaPayloadError

                    parsed[symbol] = Snapshot(
                        daily_bar=self._parse_bar(cast("dict[str, Any]", daily_bar_obj)),
                        latest_quote=self._parse_quote(cast("dict[str, Any]", latest_quote_obj)),
                        latest_trade=self._parse_trade(cast("dict[str, Any]", latest_trade_obj)),
                        minute_bar=self._parse_bar(cast("dict[str, Any]", minute_bar_obj)),
                        previous_daily_bar=self._parse_bar(
                            cast("dict[str, Any]", prev_daily_bar_obj)
                        ),
                    )

            return Snapshots(snapshots=parsed)

        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def get_historical_trades(
        self,
        symbols: list[str],
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
        feed: str | None = "iex",
    ) -> HistoricalTrades:
        """
        Fetch historical trade data for a given symbol.

        :param symbol: The stock symbol to fetch trades for.
        :param start: Start date in ISO format (YYYY-MM-DD).
        :param end: End date in ISO format (YYYY-MM-DD).
        :param limit: Maximum number of records to return.
        :return: JSON response containing trade data.
        """
        params = {
            "symbols": symbols,
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ") if start else None,
            "end": end.strftime("%Y-%m-%dT%H:%M:%SZ") if end else None,
            "limit": limit,
            "feed": feed,
        }
        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/trades",
            options=RequestOptions(params=params),
        )

        try:
            trades_by_symbol = data.get("trades") or {}

            parsed: dict[str, Any] = {}
            if isinstance(trades_by_symbol, Mapping):
                for symbol, list in trades_by_symbol.items():
                    parsed_trades = []
                    parsed_trades.append(
                        [self._parse_trade(trade) for trade in list],
                    )

                    parsed[symbol] = parsed_trades

            return HistoricalTrades(
                trades=parsed,
                next_page_token=self._req_str(data, "next_page_token"),
            )
        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def get_latest_trades(self, symbols: list[str]) -> dict[str, Any]:
        """
        Fetch the latest trade data for a given symbol.

        :param symbols: The stock symbols to fetch the latest trade for.
        :return: JSON response containing the latest trade data.
        """

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/stocks/trades/latest",
            options=RequestOptions(params={"symbols": symbols}),
        )
        try:
            trades_by_symbol = data.get("trades") or {}

            parsed: dict[str, Any] = {}
            if isinstance(trades_by_symbol, Mapping):
                for symbol, list in trades_by_symbol.items():
                    parsed_trades = []
                    parsed_trades.append(
                        self._parse_trade(list),
                    )

                    parsed[symbol] = parsed_trades

            return {
                "trades": parsed,
                "currency": data.get("currency"),
            }
        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def get_most_active_stocks(
        self,
        by: str | None = "volume",
        top: int | None = 10,
    ) -> MostActiveStocks:
        """
        Fetch the most active stocks.

        :param limit: Maximum number of records to return.
        :return: JSON response containing most active stocks data.
        """
        params = {"by": by, "top": top}

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v1beta1/screener/stocks/most-actives",
            options=RequestOptions(params=params),
        )

        try:
            parsed: dict[str, Any] = {}
            data = data.get("most_actives", [])
            if isinstance(data, Mapping):
                for stock in data:
                    symbol = self._req_str(stock, "symbol")
                    parsed[symbol] = MostActiveStock(
                        symbol=symbol,
                        volume=self._req_int(stock, "volume"),
                        trade_count=self._req_int(stock, "trade_count"),
                    )

            return MostActiveStocks(
                most_active_stocks=list(parsed.values()),
            )

        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e

    def _as_dict_any(self, m: Mapping[str, object]) -> dict[str, Any]:
        # copies into a real dict, satisfies type checker and avoids lying about mutability
        return dict(m)

    def get_top_market_movers(self, top: int = 10) -> TopMarketMovers:
        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v1beta1/screener/stocks/movers",
            options=RequestOptions(params={"top": top}),
        )

        if not isinstance(data, Mapping):
            raise JsonResponseError()

        data_map = cast("Mapping[str, object]", data)
        data_d = self._as_dict_any(data_map)

        gainers_obj = data_map.get("gainers")
        losers_obj = data_map.get("losers")

        gainers: Sequence[object] = []
        if isinstance(gainers_obj, Sequence) and not isinstance(gainers_obj, (str, bytes)):
            gainers = gainers_obj

        losers: Sequence[object] = []
        if isinstance(losers_obj, Sequence) and not isinstance(losers_obj, (str, bytes)):
            losers = losers_obj

        def parse_movers(seq: Sequence[object]) -> list[Mover]:
            out: list[Mover] = []
            for item in seq:
                if not isinstance(item, Mapping):
                    raise InvalidAlpacaPayloadError
                mover_d = self._as_dict_any(cast("Mapping[str, object]", item))
                out.append(
                    Mover(
                        symbol=self._req_str(mover_d, "symbol"),
                        percentage_change=self._req_float(mover_d, "percent_change"),
                        change=self._req_float(mover_d, "change"),
                        price=self._req_float(mover_d, "price"),
                    )
                )
            return out

        return TopMarketMovers(
            gainers=parse_movers(gainers),
            losers=parse_movers(losers),
            market_type=self._req_str(data_d, "market_type"),
            last_updated=self._parse_ts(self._req_str(data_d, "last_updated")),
        )

    def _parse_crypto_bars_list(self, raw: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        if not raw:
            return []

        out: list[dict[str, Any]] = []
        for b in raw:
            out.append(
                {
                    "timestamp": self._parse_ts(self._req_str(b, "t")),
                    "open": self._req_float(b, "o"),
                    "high": self._req_float(b, "h"),
                    "low": self._req_float(b, "l"),
                    "close": self._req_float(b, "c"),
                    "volume": self._req_float(b, "v"),
                    "number_of_trades": self._req_int(b, "n"),
                    "volume_weighted_average_price": self._req_float(b, "vw"),
                }
            )
        return out

    def crypto_get_historical_bars(
        self,
        loc: str,
        symbols: list[str],
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = 1000,
        page_token: str | None = None,
        sort: str = "asc",
    ) -> HistoricalBars:
        if sort not in ("asc", "desc"):
            raise InvalidSortParameterError(sort)

        if limit is not None and not (CRYPTO_MIN_DATA_POINTS <= limit <= CRYPTO_MAX_DATA_POINTS):
            raise InvalidLimitParameterError(limit)

        params: dict[str, str | int | float | list[str]] = {
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "sort": sort,
        }

        if limit is not None:
            params["limit"] = int(limit)
        if start is not None:
            params["start"] = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end is not None:
            params["end"] = end.strftime("%Y-%m-%dT%H:%M:%SZ")
        if page_token is not None:
            params["page_token"] = page_token

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path=f"/v1beta3/crypto/{loc}/bars",
            options=RequestOptions(params=params),
        )

        try:
            bars_raw = data.get("bars")
            if not isinstance(bars_raw, Mapping):
                raise InvalidAlpacaPayloadError

            parsed: dict[str, Any] = {}
            for symbol, bar_list_obj in bars_raw.items():
                if not isinstance(symbol, str):
                    raise InvalidAlpacaPayloadError
                if not isinstance(bar_list_obj, list):
                    raise InvalidAlpacaPayloadError

                parsed[symbol] = [self._parse_crypto_bars_list(bar_list_obj)]

            return HistoricalBars(bars=parsed)

        except (TypeError, KeyError) as e:
            pprint(data)
            raise JsonResponseError() from e
