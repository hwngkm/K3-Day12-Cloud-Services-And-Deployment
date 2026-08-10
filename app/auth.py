"""CP3 — Xác thực bằng API key.

Public URL = ai cũng gọi được. Không có lớp này, hóa đơn LLM của bạn do
người lạ quyết định.
"""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings

ANONYMOUS_USER = "anonymous"


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    settings = get_settings()
    valid_keys = {
        settings.gemini_api_key,
        settings.gemini_api_key_2,
        settings.gemini_api_key_3,
        settings.gemini_api_key_4,
        settings.gemini_api_key_5,
    }
    valid_keys = {k for k in valid_keys if k}
    if not x_api_key or not any(secrets.compare_digest(x_api_key, k) for k in valid_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
        )
    return x_user_id if x_user_id is not None else ANONYMOUS_USER
