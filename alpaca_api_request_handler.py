from typing import Any

from requests import Session

from alpaca_api_exceptions import JsonResponseError, UnknownError


def alpaca_api_request(
    base_url: str, session: Session, method: str, path: str, **kwargs: Any
) -> dict[str, Any]:
    url = f"{base_url}{path}"
    resp = session.request(method, url, **kwargs)

    # For error handling
    match resp.status_code:
        case 200:
            try:
                resp.json()
            except Exception:
                raise JsonResponseError() from None
            return resp.json()

        case 204:
            return {}

        case _:
            raise UnknownError(message_body=str(resp.status_code)) from None
