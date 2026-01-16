from collections.abc import Mapping
from typing import Any, cast

from requests import Session

from alpaca_api_request_handler import (
    BadRequestError,
    InsufficientCryptoQuantityError,
    InvalidAlpacaPayloadError,
    InvalidQuantityError,
    JsonResponseError,
    RequestOptions,
    alpaca_api_request,
)
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
    ) -> None:
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

    def get_account(self) -> GetAccountResponse:
        """Fetch your account information."""

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/account",
        )

        if not isinstance(data, Mapping):
            raise JsonResponseError()

        allowed = set(GetAccountResponse.__annotations__.keys())

        payload: dict[str, Any] = {
            k: v for k, v in data.items() if isinstance(k, str) and k in allowed
        }

        return GetAccountResponse(**payload)

    def get_assets(
        self,
        status: str | None = None,
        asset_class: str | None = None,
        exchange: str | None = None,
    ) -> GetAssetsResponse:
        """List all assets, optionally filtered by status/class/exchange."""

        params: dict[str, str | int | float | list[str]] = {}
        if status is not None:
            params["status"] = status
        if asset_class is not None:
            params["asset_class"] = asset_class
        if exchange is not None:
            params["exchange"] = exchange

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/assets",
            options=RequestOptions(params=params),
        )

        if not isinstance(data, list):
            raise JsonResponseError()

        assets: list[Asset] = []
        asset_fields = set(Asset.__annotations__.keys())

        for item in data:
            if not isinstance(item, Mapping):
                raise InvalidAlpacaPayloadError

            row = item  # Mapping[str, object]
            payload: dict[str, Any] = {}

            for k in asset_fields:
                v = row.get(k)
                payload[k] = v

            assets.append(Asset(**payload))

        return GetAssetsResponse(assets=assets)

    def get_asset(self, symbol: str) -> Asset:
        """Fetch a single asset by symbol or asset ID."""
        data = alpaca_api_request(
            base_url=self.base_url, session=self.session, method="GET", path=f"/v2/assets/{symbol}"
        )

        allowed = set(Asset.__annotations__.keys())

        if not isinstance(data, Mapping):
            raise JsonResponseError()

        payload: dict[str, Any] = {k: v for k, v in data.items() if k in allowed}

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
    def _normalise_quantity(qty: int, asset: str) -> str | int | None:
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
        qty: int | None = None,
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
    ) -> Order:
        # ---- basic validation that matches Alpaca rules ----
        if qty is not None and notional is not None:
            raise ValueError("Provide either qty or notional, not both.")

        if type in ("limit", "stop_limit") and limit_price is None:
            raise ValueError("limit_price is required for limit and stop_limit orders.")

        if type in ("stop", "stop_limit") and stop_price is None:
            raise ValueError("stop_price is required for stop and stop_limit orders.")

        if type == "trailing_stop" and trail_price is None and trail_percent is None:
            raise ValueError("trail_price or trail_percent is required for trailing_stop orders.")

        if extended_hours and not (type == "limit" and time_in_force == "day"):
            raise ValueError("extended_hours only works with type='limit' and time_in_force='day'.")

        # If using bracket/oco/oto, Alpaca expects order_class + take_profit/stop_loss rules.
        # Do not send take_profit/stop_loss unless order_class is set appropriately.
        if (take_profit is not None or stop_loss is not None) and (
            order_class is None or order_class in ("", "simple")
        ):
            raise ValueError(
                "take_profit/stop_loss require order_class like 'bracket', 'oto', or 'oco'."
            )

        # ---- build JSON payload (match Alpaca: strings for numeric fields) ----
        body: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "time_in_force": time_in_force,
        }

        if qty is not None:
            body["qty"] = str(qty)
        if notional is not None:
            body["notional"] = str(notional)

        if limit_price is not None:
            body["limit_price"] = str(limit_price)
        if stop_price is not None:
            body["stop_price"] = str(stop_price)
        if trail_price is not None:
            body["trail_price"] = str(trail_price)
        if trail_percent is not None:
            body["trail_percent"] = str(trail_percent)

        # Only include extended_hours when True (don’t send it always)
        if extended_hours:
            body["extended_hours"] = True

        if client_order_id is not None:
            body["client_order_id"] = client_order_id

        # order_class: Alpaca accepts "" or "simple" for basic
        if order_class is not None:
            body["order_class"] = order_class

        tp_json: dict[str, str] | None = None
        if take_profit is not None:
            lp = take_profit.get("limit_price")
            if lp is None:
                raise ValueError("take_profit requires limit_price")
            tp_json = {"limit_price": str(lp)}

        sl_json: dict[str, str] | None = None
        if stop_loss is not None:
            sp = stop_loss.get("stop_price")
            if sp is None:
                raise ValueError("stop_loss requires stop_price")
            sl_json = {"stop_price": str(sp)}
            lp2 = stop_loss.get("limit_price")
            if lp2 is not None:
                sl_json["limit_price"] = str(lp2)

        if tp_json is not None:
            body["take_profit"] = tp_json
        if sl_json is not None:
            body["stop_loss"] = sl_json

        resp = alpaca_api_request(
            base_url=self.base_url,  # MUST be paper-api or api, not data.alpaca.markets
            session=self.session,
            method="POST",
            path="/v2/orders",
            options=RequestOptions(json=body),
        )

        if not isinstance(resp, Mapping):
            raise JsonResponseError()

        resp_d = cast("dict[str, Any]", dict(resp))

        allowed = set(Order.__annotations__.keys())
        payload: dict[str, Any] = {k: v for k, v in resp_d.items() if k in allowed}

        cls = resp_d.get("class")
        if cls is None or isinstance(cls, str):
            payload["asset_class"] = cls
        else:
            raise InvalidAlpacaPayloadError

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
        params_raw: dict[str, str | int | float | list[str] | None] = {
            "status": status,
            "limit": limit,
            "after": after,
            "until": until,
            "direction": direction,
            "nested": "true" if nested else "false",
            "symbol": symbol,
            "side": side,
        }

        params: dict[str, str | int | float | list[str]] = {
            k: v for k, v in params_raw.items() if v is not None
        }

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/orders",
            options=RequestOptions(params=params),
        )

        if not isinstance(data, list):
            raise JsonResponseError()

        orders: list[Order] = []
        allowed = set(Order.__annotations__.keys())

        for item in data:
            if not isinstance(item, Mapping):
                raise InvalidAlpacaPayloadError

            payload: dict[str, Any] = {
                k: v for k, v in item.items() if isinstance(k, str) and k in allowed
            }

            # Map Alpaca's "class" -> your "asset_class"
            cls = item.get("class")
            if cls is None:
                payload["asset_class"] = None
            elif isinstance(cls, str):
                payload["asset_class"] = cls
            else:
                raise InvalidAlpacaPayloadError

            orders.append(Order(**payload))

        return AllOrdersResponse(orders=orders)

    def delete_all_orders(self) -> DeleteAllOrdersResponse:
        """
        Cancel all open orders.
        """
        data = alpaca_api_request(
            base_url=self.base_url, session=self.session, method="DELETE", path="/v2/orders"
        )

        rows = cast("list[dict[str, Any]]", data)

        orders: list[DeleteOrderResponse] = []
        order_fields = set(DeleteOrderResponse.__annotations__.keys())

        for row in rows:
            payload = {k: row.get(k) for k in order_fields}
            orders.append(DeleteOrderResponse(**payload))

        return DeleteAllOrdersResponse(DeletedOrders=orders)

    def get_order_by_client_order_id(self, client_order_id: str) -> Order:
        """
        Fetch an order by client order ID.
        """
        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path=f"/v2/orders:by_client_order_id?client_order_id={client_order_id}",
        )

        allowed = set(Order.__annotations__.keys())

        if not isinstance(data, Mapping):
            raise JsonResponseError()

        payload: dict[str, Any] = {k: v for k, v in data.items() if k in allowed}

        payload["asset_class"] = data.get("class")

        return Order(**payload)

    def get_order_by_id(self, order_id: str) -> Order:
        """
        Fetch an order by its ID.
        """
        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path=f"/v2/orders/{order_id}",
        )

        allowed = set(Order.__annotations__.keys())

        if not isinstance(data, Mapping):
            raise JsonResponseError()

        payload: dict[str, Any] = {k: v for k, v in data.items() if k in allowed}

        payload["asset_class"] = data.get("class")

        return Order(**payload)

    def replace_order_by_id(
        self,
        order_id: str,
        qty: int | None = None,
        time_in_force: str | None = None,
        limit_price: float | None = None,
        stop_price: float | None = None,
        trail_price: float | None = None,
        client_order_id: str | None = None,
    ) -> Order:
        """Replace an existing order by its ID."""

        body_raw: dict[str, Any] = {
            "qty": qty,
            "time_in_force": time_in_force,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "trail_price": trail_price,
            "client_order_id": client_order_id,
        }
        body: dict[str, Any] = {k: v for k, v in body_raw.items() if v is not None}

        resp = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="PATCH",
            path=f"/v2/orders/{order_id}",
            options=RequestOptions(json=body),  # <-- use RequestOptions consistently
        )

        if not isinstance(resp, Mapping):
            raise JsonResponseError()

        allowed = set(Order.__annotations__.keys())

        payload: dict[str, Any] = {
            k: v for k, v in resp.items() if isinstance(k, str) and k in allowed
        }

        # Alpaca response key "class" -> your model key "asset_class"
        cls = resp.get("class")
        if cls is None:
            payload["asset_class"] = None
        elif isinstance(cls, str):
            payload["asset_class"] = cls
        else:
            raise InvalidAlpacaPayloadError

        return Order(**payload)

    def cancel_order_by_id(self, order_id: str) -> None:
        """
        Cancel an order by its ID.

        This api call doesn't return anything, but errors if the order can't be cancelled.
        """

        alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="DELETE",
            path=f"/v2/orders/{order_id}",
        )

    def get_all_positions(self) -> dict[str, Any]:
        """
        List all positions.
        """
        return alpaca_api_request(
            base_url=self.base_url, session=self.session, method="GET", path="/v2/positions"
        )

    def close_all_positions(self, cancel_orders: bool = True) -> dict[str, Any]:
        """Close all open positions, optionally canceling associated orders."""

        params: dict[str, str | int | float | list[str]] = {
            "cancel_orders": "true" if cancel_orders else "false"
        }

        data = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="DELETE",
            path="/v2/positions",
            options=RequestOptions(params=params),
        )

        if not isinstance(data, dict):
            raise JsonResponseError()

        return data

    def get_open_position(self, symbol: str) -> dict[str, Any]:
        """
        Fetch an open position by symbol.
        """
        return alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path=f"/v2/positions/{symbol}",
        )

    def close_position(
        self,
        symbol_or_asset_id: str,
        qty: int | None = None,
        percentage: int | None = None,
    ) -> dict[str, Any]:
        """
        Close a position by symbol or asset ID.
        Provide either qty or percentage (not both). If neither is provided, closes the full position.
        """
        if qty is not None and percentage is not None:
            raise BadRequestError()

        body: dict[str, Any] = {}
        if qty is not None:
            body["qty"] = qty
        if percentage is not None:
            body["percentage"] = percentage

        resp = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="DELETE",
            path=f"/v2/positions/{symbol_or_asset_id}",
            options=RequestOptions(json=body if body else None),
        )

        if not isinstance(resp, dict):
            raise JsonResponseError()

        return resp

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
        """Fetch account portfolio history."""

        params_raw: dict[str, str | None] = {
            "period": period,
            "timeframe": timeframe,
            "date_start": date_start,
            "date_end": date_end,
            "extended_hours": "true" if extended_hours else "false",
        }
        params: dict[str, str | int | float | list[str]] = {
            k: v for k, v in params_raw.items() if v is not None
        }

        resp = alpaca_api_request(
            base_url=self.base_url,
            session=self.session,
            method="GET",
            path="/v2/account/portfolio/history",
            options=RequestOptions(params=params),
        )

        if not isinstance(resp, dict):
            raise JsonResponseError()

        return resp

    def get_market_clock(self) -> dict[str, Any]:
        """
        Fetch the current market clock status.
        """
        return alpaca_api_request(
            base_url=self.base_url, session=self.session, method="GET", path="/v2/clock"
        )
