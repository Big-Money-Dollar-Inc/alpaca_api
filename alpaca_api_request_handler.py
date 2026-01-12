from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from requests import Response, Session

HTTP_OK = 200
HTTP_NO_CONTENT = 204


class JsonResponseError(Exception):
    def __init__(self) -> None:
        super().__init__("Unable to parse JSON response")


# Exception raised for invalid 'sort' parameter
class InvalidSortParameterError(ValueError):
    def __init__(self, sort_value: str) -> None:
        super().__init__(f"sort must be 'asc' or 'desc', got '{sort_value}'")


# Exception raised for invalid 'limit' parameter
class InvalidLimitParameterError(ValueError):
    def __init__(self, limit: int) -> None:
        super().__init__(f"limit must be between 1 and 10000, got {limit}")


# Exception raised when quantity is not numeric
class InvalidQuantityError(TypeError):
    """Exception raised when quantity is invalid."""

    def __init__(self, message: str = "Quantity must be numeric") -> None:
        super().__init__(message)


# Exception raised when crypto order quantity is below minimum
class InsufficientCryptoQuantityError(ValueError):
    """Exception raised when crypto order quantity is below minimum."""

    def __init__(self, min_qty: float) -> None:
        super().__init__(f"Crypto orders require qty >= {min_qty}")


class InvalidAlpacaPayloadError(TypeError):
    """Exception raised when the Alpaca API payload received an invalid type."""

    def __init__(self, message: str = "Invalid payload received from Alpaca API") -> None:
        super().__init__(message)


class AlpacaAPIError(Exception):
    status_code: int

    def __init__(self, message: str, message_body: str = "") -> None:
        full_message = f"{message}\n{message_body}" if message_body else message
        super().__init__(full_message)


class BadRequestError(AlpacaAPIError):
    status_code = 400

    def __init__(self, message_body: str = "") -> None:
        super().__init__(
            "One of the request parameters is invalid. See the returned message for details.",
            message_body,
        )


class UnauthorizedError(AlpacaAPIError):
    status_code = 401

    def __init__(self, message_body: str = "") -> None:
        super().__init__(
            "Authentication headers are missing or invalid. Make sure you authenticate your request with a valid API key.",
            message_body,
        )


class ForbiddenError(AlpacaAPIError):
    status_code = 403

    def __init__(self, message_body: str = "") -> None:
        super().__init__("The requested resource is forbidden.", message_body)


class UnprocessableEntityError(AlpacaAPIError):
    status_code = 422

    def __init__(self, message_body: str = "") -> None:
        super().__init__("The order status is not cancelable.", message_body)


class RateLimitError(AlpacaAPIError):
    status_code = 429

    def __init__(self, message_body: str = "") -> None:
        super().__init__(
            "Too many requests. You hit the rate limit. Use the X-RateLimit headers to stay under the limit.",
            message_body,
        )


class InternalServerError(AlpacaAPIError):
    status_code = 500

    def __init__(self, message_body: str = "") -> None:
        super().__init__(
            "Internal server error. Retry later. If the issue persists, contact https://forum.alpaca.markets/",
            message_body,
        )


class UnknownError(AlpacaAPIError):
    status_code = 000

    def __init__(self, message_body: str = "") -> None:
        super().__init__(
            "Unknown error, please add this to alpaca_api_exceptions.py and alpaca_api_request_handler.py and push your changes.",
            message_body,
        )


class RequestOptions(TypedDict, total=False):
    params: dict[str, str | int | float | list[str]]
    data: bytes | str | dict[str, str]
    json: object
    headers: dict[str, str]
    timeout: float | tuple[float, float]
    allow_redirects: bool
    stream: bool
    verify: bool | str
    cert: str | tuple[str, str]
    proxies: dict[str, str]


def _safe_json(resp: Response) -> dict[str, object]:
    try:
        parsed = resp.json()
    except Exception as e:
        raise JsonResponseError() from e

    if not isinstance(parsed, dict):
        raise JsonResponseError()

    return parsed


def alpaca_api_request(
    base_url: str,
    session: Session,
    method: str,
    path: str,
    options: RequestOptions | None = None,
) -> dict[str, object]:
    url = f"{base_url}{path}"
    resp = session.request(method, url, **(options or {}))

    if resp.status_code == HTTP_OK:
        return _safe_json(resp)

    if resp.status_code == HTTP_NO_CONTENT:
        return {}

    raise UnknownError(message_body=str(resp.status_code)) from None
