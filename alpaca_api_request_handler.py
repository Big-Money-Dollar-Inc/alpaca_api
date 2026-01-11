from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from requests import Response, Session

from alpaca_api_exceptions import JsonResponseError, UnknownError

HTTP_OK = 200
HTTP_NO_CONTENT = 204


class RequestOptions(TypedDict, total=False):
    params: dict[str, str]
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
