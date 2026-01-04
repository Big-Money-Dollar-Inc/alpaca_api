# alpaca_api_exceptions.py


# Exception raised when a JSON response cannot be parsed
class JsonResponseError(Exception):
    def __init__(self):
        super().__init__("Unable to parse JSON response")


# Exception raised when a response is not 200 OK
class NonOkResponseError(Exception):
    def __init__(self, status_code: int):
        super().__init__(f"Received non-OK response: {status_code}")


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
