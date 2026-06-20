import hashlib
import hmac
import json
from datetime import datetime, timezone
from urllib.parse import urlencode

import pytest

from app.core.config import settings
from app.core.security import validate_telegram_init_data


def build_init_data(bot_token: str, **overrides: str) -> str:
    values = {
        "auth_date": str(int(datetime.now(timezone.utc).timestamp())),
        "query_id": "test-query",
        "user": json.dumps(
            {"id": 123456, "first_name": "Test", "username": "tester"},
            separators=(",", ":"),
        ),
        **overrides,
    }
    check_string = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    values["hash"] = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


def test_valid_telegram_init_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "test-token")
    result = validate_telegram_init_data(build_init_data("test-token"))
    assert result.user.id == 123456
    assert result.user.username == "tester"


def test_rejects_tampered_telegram_init_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "test-token")
    init_data = build_init_data("test-token").replace("tester", "attacker")
    with pytest.raises(ValueError, match="signature"):
        validate_telegram_init_data(init_data)
