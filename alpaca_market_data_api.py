from datetime import datetime
from requests import Session
from typing import List, Optional, Dict, Any

class AlpacaMarketDataAPI:
    """
    Alpaca REST Client for accessing Alpaca's market data API.
    """
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        request_session: Optional[Session] = None
    ):
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
    def _headers(api_key: str, api_secret: str) -> Dict[str, str]:
        return {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": api_secret,
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.session.request(method, url, **kwargs)

        OK_RESPONSE_CODE = 200

        if resp.status_code != OK_RESPONSE_CODE:
            try:
                error_data = resp.json()
            except ValueError:
                error_data = {"error": "Unknown error occurred"}
            raise Exception(f"Error {resp.status_code}: {error_data.get('message', 'No message provided')}")

        return resp.json()

    def get_historical_auctions(
        self,
        symbols: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch historical auction data for a given symbol.
        
        :param symbol: The stock symbol to fetch auctions for.
        :param start: Start date in ISO format (YYYY-MM-DD).
        :param end: End date in ISO format (YYYY-MM-DD).
        :param limit: Maximum number of records to return.
        :return: JSON response containing auction data.
        """
        params = {
            "symbols": symbols,
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ") if start else None,
            "end": end.strftime("%Y-%m-%dT%H:%M:%SZ") if end else None,
            "limit": limit
        }
        return self._request("GET", "/v2/stocks/auctions", params=params)

    def get_historical_bars(
        self,
        symbols: str,
        timeframe: str = "1H",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
        feed: Optional[str] = "iex",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch historical bar data for a given symbol.
        
        :param symbol: The stock symbol to fetch bars for.
        :param start: Start date in ISO format (YYYY-MM-DD).
        :param end: End date in ISO format (YYYY-MM-DD).
        :param limit: Maximum number of records to return.
        :return: JSON response containing bar data.
        """
        params: Dict[str, Any] = {
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
        return self._request("GET", "/v2/stocks/bars", params=params)

    def get_latest_bars(
        self,
        symbols: List[str]
    ) -> Dict[str, Any]:
        """
        Fetch the latest bar data for one or more symbols
        (always returns a dict under the "bars" key).
        """
        params = {"symbols": ",".join(symbols)}
        return self._request("GET", "/v2/stocks/bars/latest", params=params)

    def get_condition_codes(
        self,
        ticktype: Optional[str] = "trade",
        tape: Optional[str] = "A"
    ) -> Dict[str, Any]:
        """
        Fetch the condition codes used in market data.
        
        :return: JSON response containing condition codes.
        """
        params = { "tape": tape }
        return self._request("GET", f"/v2/stocks/meta/conditions/{ticktype}", params=params)

    def get_exchange_codes(
        self
    ) -> Dict[str, Any]:
        """
        Fetch the exchange codes used in market data.
        
        :return: JSON response containing exchange codes.
        """
        return self._request("GET", "/v2/stocks/meta/exchanges")

    def get_historical_quotes(
        self,
        symbols: List[str],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
        feed: Optional[str] = "iex"
    ) -> Dict[str, Any]:
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
            "feed": feed
        }
        return self._request("GET", "/v2/stocks/quotes", params=params)

    def get_latest_quotes(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Fetch the latest quote data for a given symbol.
        
        :param symbol: The stock symbol to fetch the latest quote for.
        :return: JSON response containing the latest quote data.
        """
        params = {"symbols": symbol}
        return self._request("GET", "/v2/stocks/quotes/latest", params=params)

    def get_snapshots(
        self,
        symbols: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch snapshots for one or more symbols.
        
        :param symbols: Comma-separated list of stock symbols.
        :return: JSON response containing snapshot data.
        """
        params = {"symbols": symbols} if symbols else {}
        return self._request("GET", "/v2/stocks/snapshots", params=params)

    def get_historical_trades(
        self,
        symbols: List[str],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
        feed: Optional[str] = "iex"
    ) -> Dict[str, Any]:
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
            "feed": feed
        }
        return self._request("GET", "/v2/stocks/trades", params=params)

    def get_latest_trades(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Fetch the latest trade data for a given symbol.
        
        :param symbol: The stock symbol to fetch the latest trade for.
        :return: JSON response containing the latest trade data.
        """
        params = {"symbols": symbol}
        return self._request("GET", "/v2/stocks/trades/latest", params=params)

    def get_most_active_stocks(
        self,
        by: Optional[str] = "volume",
        top: Optional[int] = 10,
    ) -> Dict[str, Any]:
        """
        Fetch the most active stocks.
        
        :param limit: Maximum number of records to return.
        :return: JSON response containing most active stocks data.
        """
        params = {"by": by, "top": top}
        return self._request("GET", "/v1beta1/screener/stocks/most-actives", params=params)

    def get_top_market_movers(
        self,
        top: Optional[int] = 10,
    ) -> Dict[str, Any]:
        """
        Fetch top market movers in a given direction.
        
        :param direction: 'up' for gainers, 'down' for losers.
        :param limit: Maximum number of records to return.
        :return: JSON response containing top market movers data.
        """
        params = {"top": top}
        return self._request("GET", "/v1beta1/screener/stocks/movers", params=params)

    def crypto_get_historical_bars(
        self,
        loc: str,
        symbols: List[str],
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = 1000,
        page_token: Optional[str] = None,
        sort: str = "asc",
    ) -> Dict[str, Any]:
        """
        Fetch historical crypto bars from Alpaca v1beta3.

        :param loc: Crypto data location, for example "us".
        :param symbols: List of symbols, for example ["BTC/USD", "ETH/USD"].
        :param timeframe: Bar aggregation, for example "1Min", "5Min", "1H", "1D", "1W", "3M".
        :param start: Inclusive start time as datetime (UTC). If provided, formatted RFC3339.
        :param end: Inclusive end time as datetime (UTC). If provided, formatted RFC3339.
        :param limit: Max data points across all symbols, 1 to 10000. Default 1000.
        :param page_token: Pagination token from prior response.
        :param sort: "asc" or "desc". Default "asc".
        :return: JSON response with "bars" and optional "next_page_token".
        """
        if sort not in ("asc", "desc"):
            raise ValueError("sort must be 'asc' or 'desc'")
        
        LOWER_LIMIT = 1
        UPPER_LIMIT = 10000

        if limit is not None and not (LOWER_LIMIT <= int(limit) <= UPPER_LIMIT):
            raise ValueError("limit must be between 1 and 10000")

        params: Dict[str, Any] = {
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
        if page_token:
            params["page_token"] = page_token

        # Endpoint: /v1beta3/crypto/{loc}/bars
        return self._request("GET", f"/v1beta3/crypto/{loc}/bars", params=params)
