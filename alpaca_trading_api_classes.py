from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GetAccountResponse:
    id: str
    status: str

    account_number: str | None = None

    currency: str | None = None

    cash: str | None = None
    portfolio_value: str | None = None
    non_marginable_buying_power: str | None = None
    accrued_fees: str | None = None
    pending_transfer_in: str | None = None
    pending_transfer_out: str | None = None

    pattern_day_trader: bool | None = None
    trade_suspended_by_user: bool | None = None
    trading_blocked: bool | None = None
    transfers_blocked: bool | None = None
    account_blocked: bool | None = None

    created_at: str | None = None

    shorting_enabled: bool | None = None

    long_market_value: str | None = None
    short_market_value: str | None = None
    position_market_value: str | None = None

    equity: str | None = None
    last_equity: str | None = None

    multiplier: str | None = None
    buying_power: str | None = None
    effective_buying_power: str | None = None

    initial_margin: str | None = None
    maintenance_margin: str | None = None
    last_maintenance_margin: str | None = None

    sma: str | None = None

    daytrade_count: int | None = None
    daytrading_buying_power: str | None = None
    regt_buying_power: str | None = None
    bod_dtbp: str | None = None

    options_buying_power: str | None = None
    options_approved_level: int | None = None
    options_trading_level: int | None = None

    intraday_adjustments: str | None = None
    pending_reg_taf_fees: str | None = None

    balance_asof: str | None = None

    crypto_status: str | None = None
    crypto_tier: int | None = None

    admin_configurations: dict | None = None
    user_configurations: dict | None = None


@dataclass
class Asset:
    id: int | None

    asset_class: str | None

    exchange: str | None

    symbol: str | None
    name: str | None
    status: str | None

    tradable: bool | None
    marginable: bool | None
    shortable: bool | None
    easy_to_borrow: bool | None
    fractionable: bool | None

    attributes: list[str] | None

    cusip: str | None = None

    maintenance_margin_requirement: float | None = None

    margin_requirement_long: str | None = None
    margin_requirement_short: str | None = None


@dataclass
class GetAssetsResponse:
    assets: list[Asset]


@dataclass
class Order:
    id: str | None
    client_order_id: str | None
    asset_id: str | None
    symbol: str | None
    asset_class: str | None
    filled_qty: str | None
    order_class: str | None
    time_in_force: str | None
    type: str | None
    status: str | None
    extended_hours: bool | None

    created_at: str | None
    updated_at: str | None = None
    submitted_at: str | None = None
    filled_at: str | None = None
    expired_at: str | None = None
    canceled_at: str | None = None
    failed_at: str | None = None
    replaced_at: str | None = None

    replaced_by: str | None = None
    replaces: str | None = None

    notional: str | None = None
    qty: str | None = None

    filled_avg_price: str | None = None

    order_type: str | None = None  # deprecated

    side: str | None = None

    limit_price: str | None = None
    stop_price: str | None = None

    legs: list[Order] | None = None

    trail_percent: str | None = None
    trail_price: str | None = None
    hwm: str | None = None

    position_intent: str | None = None


@dataclass
class AllOrdersResponse:
    orders: list[Order]


@dataclass
class DeleteOrderResponse:
    id: str | None
    status: int | None


@dataclass
class DeleteAllOrdersResponse:
    DeletedOrders: list[DeleteOrderResponse] | None


@dataclass
class Position:
    asset_id: str
    symbol: str

    asset_class: str

    avg_entry_price: str
    qty: str
    qty_available: str

    side: str

    market_value: str
    cost_basis: str

    unrealized_pl: str
    unrealized_plpc: str

    unrealized_intraday_pl: str
    unrealized_intraday_plpc: str

    current_price: str
    lastday_price: str
    change_today: str

    asset_marginable: bool

    exchange: str | None = None


@dataclass
class GetAllPositionsResponse:
    positions: list[Position]


@dataclass
class CloseAllPositionsResponse:
    closed_positions: list[Order]


@dataclass
class GetAccountPortfolioHistoryResponse:
    timestamp: list[int]

    equity: list[float]
    profit_loss: list[float]
    profit_loss_pct: list[float]
    timeframe: str

    base_value: float
    base_value_asof: str | None = None

    cashflow: dict[str, list[float]] | None = None
