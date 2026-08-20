from typing import Any


def success(data: Any, meta: dict | None = None) -> dict:
    payload: dict[str, Any] = {"success": True, "data": data}
    if meta is not None:
        payload["meta"] = meta
    return payload
