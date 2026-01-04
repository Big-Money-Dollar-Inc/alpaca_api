from requests import Session
from typing import Optional, Dict, Any

CRYPTO_MIN_ORDER_QTY = 0.0001

class AlpacaTradingAPI:
    """
    Alpaca REST Client for accessing Alpaca's trading API.
    """
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        paper: bool = True,
        request_session: Optional[Session] = None
    ):
        """
        :param api_key: Your Alpaca API key ID.
        :param api_secret: Your Alpaca API secret.
        :param paper: If True, use paper trading endpoints.
        """
        self.base_url = (
            "https://paper-api.alpaca.markets"
            if paper else
            "https://api.alpaca.markets"
        )
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
        return resp.json()

    def get_account(self) -> Dict[str, Any]:
        """Fetch your account information."""
        return self._request("GET", "/v2/account")

    def get_assets(
        self,
        status: Optional[str] = None,
        asset_class: Optional[str] = None,
        exchange: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all assets, optionally filtered by status/class/exchange."""
        params = {
            k: v for k, v in {
                "status": status,
                "asset_class": asset_class,
                "exchange": exchange
            }.items() if v is not None
        }
        return self._request("GET", "/v2/assets", params=params)

    def get_asset(self, symbol: str) -> Dict[str, Any]:
        """Fetch a single asset by symbol or asset ID."""
        return self._request("GET", f"/v2/assets/{symbol}")

    def get_option_contracts(self) -> Dict[str, Any]:
        """
        List option contracts.
        """
        raise NotImplementedError("Option contracts API not implemented yet.")

    def get_option_contract(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch a single option contract by symbol or ID.
        """
        raise NotImplementedError("Option contract API not implemented yet.")

    def get_us_treasuries(self) -> Dict[str, Any]:
        """
        List US Treasury offerings.
        """
        raise NotImplementedError("US Treasuries API not implemented yet.")

    def get_announcements(self) -> Dict[str, Any]:
        """
        List corporate announcements.
        """
        raise NotImplementedError("Announcements API not implemented yet.")

    def get_announcement(self) -> Dict[str, Any]:
        """
        Fetch a single corporate announcement.
        """
        raise NotImplementedError("Announcements API not implemented yet.")

    @staticmethod
    def _normalise_symbol(symbol: str, asset: str) -> str:
        cleaned = str(symbol).upper().strip()
        if str(asset).lower() == "crypto":
            return cleaned.replace("/", "").replace("-", "")
        return cleaned

    @staticmethod
    def _normalise_quantity(qty: Any, asset: str) -> Optional[str | int]:
        if qty is None:
            return None
        try:
            qty_value = float(qty)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be numeric")
        if qty_value <= 0:
            raise ValueError("Quantity must be positive")
        if str(asset).lower() == "crypto":
            if qty_value < CRYPTO_MIN_ORDER_QTY:
                raise ValueError(
                    f"Crypto orders require qty >= {CRYPTO_MIN_ORDER_QTY}"
                )
            normalised = f"{qty_value:.6f}".rstrip("0").rstrip(".")
            return normalised or "0.0001"
        return int(round(qty_value))

    def create_order(
        self,
        symbol: str,
        side: str,
        qty: Any = None,
        notional: Optional[float] = None,
        type: str = "market",
        time_in_force: str = "day",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        trail_percent: Optional[float] = None,
        extended_hours: bool = False,
        client_order_id: Optional[str] = None,
        order_class: Optional[str] = None,
        take_profit: Optional[Dict[str, float]] = None,
        stop_loss: Optional[Dict[str, float]] = None,
        asset: str = "stocks",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create a new order.
        """
        cleaned_symbol = self._normalise_symbol(symbol, asset)
        cleaned_qty = self._normalise_quantity(qty, asset)
        data = {
            "symbol": cleaned_symbol,
            "qty": cleaned_qty,
            "notional": notional,
            "side": side,
            "type": type,
            "time_in_force": time_in_force,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "trail_price": trail_price,
            "trail_percent": trail_percent,
            "extended_hours": extended_hours,
            "client_order_id": client_order_id,
            "order_class": order_class,
            "take_profit": take_profit,
            "stop_loss": stop_loss
        }
        if cleaned_qty is None:
            data.pop("qty", None)
        return self._request("POST", "/v2/orders", json=data)

    def get_all_orders(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        after: Optional[str] = None,
        until: Optional[str] = None,
        direction: Optional[str] = None,
        nested: bool = False,
        symbol: Optional[str] = None,
        side: Optional[str] = None,
        
    ) -> Dict[str, Any]:
        """
        List all orders, optionally filtered by status, symbol, side, etc.
        """
        params = {
            "status": status,
            "limit": limit,
            "after": after,
            "until": until,
            "direction": direction,
            "nested": str(nested).lower(),
            "symbol": symbol,
            "side": side
        }
        return self._request("GET", "/v2/orders", params=params)

    def delete_all_orders(self) -> Dict[str, Any]:
        """
        Cancel all open orders.
        """
        return self._request("DELETE", "/v2/orders")

    def get_order_by_client_order_id(
        self, 
        client_order_id: str
    ) -> Dict[str, Any]:
        """
        Fetch an order by client order ID.
        """
        return self._request("GET", f"/v2/orders/by_client_order_id/{client_order_id}")

    def get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """
        Fetch an order by its ID.
        """
        return self._request("GET", f"/v2/orders/{order_id}")

    def replace_order_by_id(
        self,
        order_id: str,
        qty: Optional[int] = None,
        time_in_force: Optional[str] = None,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        client_order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Replace an existing order by its ID.
        """
        data = {
            "qty": qty,
            "time_in_force": time_in_force,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "trail_price": trail_price,
            "client_order_id": client_order_id
        }
        return self._request("PATCH", f"/v2/orders/{order_id}", json=data)

    def cancel_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order by its ID.
        """
        return self._request("DELETE", f"/v2/orders/{order_id}")

    def get_all_positions(self) -> Dict[str, Any]:
        """
        List all positions.
        """
        return self._request("GET", "/v2/positions")

    def close_all_positions(
        self,
        cancel_orders: bool = True,
    ) -> Dict[str, Any]:
        """
        Close all open positions, optionally canceling associated orders.
        """
        params = {"cancel_orders": str(cancel_orders).lower()}
        return self._request("DELETE", "/v2/positions", params=params)

    def get_open_position(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch an open position by symbol.
        """
        return self._request("GET", f"/v2/positions/{symbol}")

    def close_position(self, symbol_or_asset_id: str, qty, percentage) -> Dict[str, Any]:
        """
        Close a position by symbol or asset ID, optionally specifying quantity or percentage.
        """
        data = {
            "qty": qty,
            "percentage": percentage
        }
        return self._request("DELETE", f"/v2/positions/{symbol_or_asset_id}", json=data)

    def exercise_option(self) -> Dict[str, Any]:
        """
        Exercise an option contract.
        """
        raise NotImplementedError("Option exercise API not implemented yet.")

    def get_account_portfolio_history(
        self,
        period: str = "1D",
        timeframe: str = "1Min",
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        extended_hours: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch account portfolio history.
        """
        params = {
            "period": period,
            "timeframe": timeframe,
            "date_start": date_start,
            "date_end": date_end,
            "extended_hours": str(extended_hours).lower()
        }
        return self._request("GET", "/v2/account/portfolio/history", params=params)

    def get_market_clock(self) -> Dict[str, Any]:
        """
        Fetch the current market clock status.
        """
        return self._request("GET", "/v2/clock")