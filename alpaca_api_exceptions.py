# alpaca_api_exceptions.py

# Code Exceptions for Alpaca API interactions

# Exception raised when a JSON response cannot be parsed


class JsonResponseError(Exception):
    def __init__(self):
        super().__init__("Unable to parse JSON response")


# Exception raised for invalid 'sort' parameter
class InvalidSortParameterError(ValueError):
    def __init__(self, sort_value: str):
        super().__init__(f"sort must be 'asc' or 'desc', got '{sort_value}'")


# Exception raised for invalid 'limit' parameter
class InvalidLimitParameterError(ValueError):
    def __init__(self, limit: int):
        super().__init__(f"limit must be between 1 and 10000, got {limit}")


# Exception raised when quantity is not numeric
class InvalidQuantityError(TypeError):
    """Exception raised when quantity is invalid."""

    def __init__(self, message: str = "Quantity must be numeric"):
        super().__init__(message)


# Exception raised when crypto order quantity is below minimum
class InsufficientCryptoQuantityError(ValueError):
    """Exception raised when crypto order quantity is below minimum."""

    def __init__(self, min_qty: float):
        super().__init__(f"Crypto orders require qty >= {min_qty}")


class InvalidAlpacaPayloadError(TypeError):
    """Exception raised when the Alpaca API payload received an invalid type."""

    def __init__(self, message: str = "Invalid payload received from Alpaca API"):
        super().__init__(message)


# Response Code Exceptions
# Exception raised when a response is not 200 OK
class AlpacaAPIReturnCodeError(Exception):
    def __init__(self, status_code: int, message_body: str = ""):
        message = ""
        match status_code:
            case 400:
                message = (
                    "One of the request parameters is invalid. See the returned message for details.\n "
                    + message_body
                )
            case 401:
                message = (
                    "Authentication headers are missing or invalid. Make sure you authenticate your request with a valid API key.\n "
                    + message_body
                )
            case 403:
                message = "The requested resource is forbidden.\n " + message_body
            case 429:
                message = (
                    "Too many requests. You hit the rate limit. Use the X-RateLimit-... response headers to make sure you're under the rate limit.\n "
                    + message_body
                )
            case 500:
                message = (
                    "Internal server error. We recommend retrying these later. If the issue persists, please contact us on https://forum.alpaca.markets/\n "
                    + message_body
                )
            case _:
                message = f"Received non-OK response: {status_code}\n " + message_body

        super().__init__(f"{message}")
