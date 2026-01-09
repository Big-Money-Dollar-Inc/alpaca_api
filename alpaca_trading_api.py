from typing import Any, cast

from requests import Session

from alpaca_api_exceptions import InsufficientCryptoQuantityError, InvalidQuantityError
from alpaca_trading_api_classes import (
    AllOrdersResponse,
    Asset,
    DeleteAllOrdersResponse,
    DeleteOrderResponse,
    GetAccountResponse,
    GetAssetsResponse,
    Order,
)

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
        request_session: Session | None = None,
    ):
        """
        :param api_key: Your Alpaca API key ID.
        :param api_secret: Your Alpaca API secret.
        :param paper: If True, use paper trading endpoints.
        """
        self.base_url = (
            "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        )
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

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.session.request(method, url, **kwargs)
        return resp.json()

    def get_account(self) -> GetAccountResponse:
        """Fetch your account information."""

        data = self._request("GET", "/v2/account")

        allowed = set(GetAccountResponse.__annotations__.keys())

        payload = {k: v for k, v in data.items() if k in allowed}

        return GetAccountResponse(**payload)

    def get_assets(
        self, status: str | None = None, asset_class: str | None = None, exchange: str | None = None
    ) -> GetAssetsResponse:
        """List all assets, optionally filtered by status/class/exchange."""
        params = {
            k: v
            for k, v in {"status": status, "asset_class": asset_class, "exchange": exchange}.items()
            if v is not None
        }
        data = self._request("GET", "/v2/assets", params=params)

        rows = cast(list[dict[str, Any]], data)

        assets: list[Asset] = []
        asset_fields = set(Asset.__annotations__.keys())

        for row in rows:
            payload = {k: row.get(k) for k in asset_fields}
            assets.append(Asset(**payload))

        return GetAssetsResponse(assets=assets)

    def get_asset(self, symbol: str) -> Asset:
        """Fetch a single asset by symbol or asset ID."""
        data = self._request("GET", f"/v2/assets/{symbol}")

        allowed = set(Asset.__annotations__.keys())

        payload = {k: v for k, v in data.items() if k in allowed}

        payload["asset_class"] = data.get("class")

        return Asset(**payload)

    def get_option_contracts(self) -> dict[str, Any]:
        """
        List option contracts.
        """
        raise NotImplementedError("Option contracts API not implemented yet.")

    def get_option_contract(self, symbol: str) -> dict[str, Any]:
        """
        Fetch a single option contract by symbol or ID.
        """
        raise NotImplementedError("Option contract API not implemented yet.")

    def get_us_treasuries(self) -> dict[str, Any]:
        """
        List US Treasury offerings.
        """
        raise NotImplementedError("US Treasuries API not implemented yet.")

    def get_announcements(self) -> dict[str, Any]:
        """
        List corporate announcements.
        """
        raise NotImplementedError("Announcements API not implemented yet.")

    def get_announcement(self) -> dict[str, Any]:
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
    def _normalise_quantity(qty: Any, asset: str) -> str | int | None:
        if qty is None:
            return None
        try:
            qty_value = float(qty)
        except TypeError as typeError:
            raise InvalidQuantityError() from typeError

        if qty_value <= 0:
            raise InvalidQuantityError() from None

        if str(asset).lower() == "crypto":
            if qty_value < CRYPTO_MIN_ORDER_QTY:
                raise InsufficientCryptoQuantityError(CRYPTO_MIN_ORDER_QTY) from None

            normalised = f"{qty_value:.6f}".rstrip("0").rstrip(".")

            return normalised or "0.0001"

        return round(qty_value)

    def create_order(
        self,
        symbol: str,
        side: str,
        qty: Any = None,
        notional: float | None = None,
        type: str = "market",
        time_in_force: str = "day",
        limit_price: float | None = None,
        stop_price: float | None = None,
        trail_price: float | None = None,
        trail_percent: float | None = None,
        extended_hours: bool = False,
        client_order_id: str | None = None,
        order_class: str | None = None,
        take_profit: dict[str, float] | None = None,
        stop_loss: dict[str, float] | None = None,
        asset: str = "stocks",
        **kwargs: Any,
    ) -> Order:
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
            "stop_loss": stop_loss,
        }
        if cleaned_qty is None:
            data.pop("qty", None)

        data = self._request("POST", "/v2/orders", json=data)

        allowed = set(Order.__annotations__.keys())

        payload = {k: v for k, v in data.items() if k in allowed}

        payload["asset_class"] = data.get("class")

        return Order(**payload)

    def get_all_orders(
        self,
        status: str | None = None,
        limit: int = 50,
        after: str | None = None,
        until: str | None = None,
        direction: str | None = None,
        nested: bool = False,
        symbol: str | None = None,
        side: str | None = None,
    ) -> AllOrdersResponse:
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
            "side": side,
        }
        data = self._request("GET", "/v2/orders", params=params)

        rows = cast(list[dict[str, Any]], data)

        orders: list[Order] = []
        order_fields = set(Order.__annotations__.keys())

        for row in rows:
            payload = {k: row.get(k) for k in order_fields}
            orders.append(Order(**payload))

        return AllOrdersResponse(orders=orders)

    def delete_all_orders(self) -> DeleteAllOrdersResponse:
        """
        Cancel all open orders.
        """
        data = self._request("DELETE", "/v2/orders")

        rows = cast(list[dict[str, Any]], data)

        orders: list[DeleteOrderResponse] = []
        order_fields = set(DeleteOrderResponse.__annotations__.keys())

        for row in rows:
            payload = {k: row.get(k) for k in order_fields}
            orders.append(DeleteOrderResponse(**payload))

        return DeleteAllOrdersResponse(DeletedOrders=orders)

    def get_order_by_client_order_id(self, client_order_id: str) -> dict[str, Any]:
        """
        Fetch an order by client order ID.
        """
        return self._request("GET", f"/v2/orders/by_client_order_id/{client_order_id}")

    def get_order_by_id(self, order_id: str) -> dict[str, Any]:
        """
        Fetch an order by its ID.
        """
        return self._request("GET", f"/v2/orders/{order_id}")

    def replace_order_by_id(
        self,
        order_id: str,
        qty: int | None = None,
        time_in_force: str | None = None,
        limit_price: float | None = None,
        stop_price: float | None = None,
        trail_price: float | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Replace an existing order by its ID.
        """
        data = {
            "qty": qty,
            "time_in_force": time_in_force,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "trail_price": trail_price,
            "client_order_id": client_order_id,
        }
        return self._request("PATCH", f"/v2/orders/{order_id}", json=data)

    def cancel_order_by_id(self, order_id: str) -> dict[str, Any]:
        """
        Cancel an order by its ID.
        """
        return self._request("DELETE", f"/v2/orders/{order_id}")

    def get_all_positions(self) -> dict[str, Any]:
        """
        List all positions.
        """
        return self._request("GET", "/v2/positions")

    def close_all_positions(
        self,
        cancel_orders: bool = True,
    ) -> dict[str, Any]:
        """
        Close all open positions, optionally canceling associated orders.
        """
        params = {"cancel_orders": str(cancel_orders).lower()}
        return self._request("DELETE", "/v2/positions", params=params)

    def get_open_position(self, symbol: str) -> dict[str, Any]:
        """
        Fetch an open position by symbol.
        """
        return self._request("GET", f"/v2/positions/{symbol}")

    def close_position(self, symbol_or_asset_id: str, qty, percentage) -> dict[str, Any]:
        """
        Close a position by symbol or asset ID, optionally specifying quantity or percentage.
        """
        data = {"qty": qty, "percentage": percentage}
        return self._request("DELETE", f"/v2/positions/{symbol_or_asset_id}", json=data)

    def exercise_option(self) -> dict[str, Any]:
        """
        Exercise an option contract.
        """
        raise NotImplementedError("Option exercise API not implemented yet.")

    def get_account_portfolio_history(
        self,
        period: str = "1D",
        timeframe: str = "1Min",
        date_start: str | None = None,
        date_end: str | None = None,
        extended_hours: bool = False,
    ) -> dict[str, Any]:
        """
        Fetch account portfolio history.
        """
        params = {
            "period": period,
            "timeframe": timeframe,
            "date_start": date_start,
            "date_end": date_end,
            "extended_hours": str(extended_hours).lower(),
        }
        return self._request("GET", "/v2/account/portfolio/history", params=params)

    def get_market_clock(self) -> dict[str, Any]:
        """
        Fetch the current market clock status.
        """
        return self._request("GET", "/v2/clock")
