import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl

from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.telegram import TelegramWebAppUser, ValidatedTelegramInitData


def validate_telegram_init_data(init_data: str) -> ValidatedTelegramInitData:
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured")

    values = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    received_hash = values.pop("hash", None)
    if not received_hash:
        raise ValueError("initData does not contain hash")

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(values.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        settings.TELEGRAM_BOT_TOKEN.encode(),
        hashlib.sha256,
    ).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise ValueError("Invalid initData signature")

    try:
        auth_timestamp = int(values["auth_date"])
        auth_date = datetime.fromtimestamp(auth_timestamp, tz=timezone.utc)
        telegram_user = TelegramWebAppUser.model_validate_json(values["user"])
    except (KeyError, ValueError, ValidationError, json.JSONDecodeError) as error:
        raise ValueError("Invalid initData payload") from error

    age = datetime.now(timezone.utc) - auth_date
    if age < timedelta(seconds=-30) or age > timedelta(
        seconds=settings.TELEGRAM_AUTH_MAX_AGE_SECONDS
    ):
        raise ValueError("initData is expired")

    return ValidatedTelegramInitData(
        auth_date=auth_date,
        hash=received_hash,
        signature=values.get("signature"),
        query_id=values.get("query_id"),
        user=telegram_user,
        start_param=values.get("start_param"),
        chat_instance=values.get("chat_instance"),
        chat_type=values.get("chat_type"),
    )


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "token_type": "access", "exp": expires_at},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_user_id_from_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as error:
        raise ValueError("Invalid token") from error

    if payload.get("token_type") != "access" or payload.get("sub") is None:
        raise ValueError("Invalid token payload")
    return int(payload["sub"])
