from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelegramInitDataRequest(BaseModel):
    """Raw initData received from Telegram.WebApp.initData.

    The backend must validate this string with the bot token before trusting any
    user fields parsed from it.
    """

    init_data: str = Field(alias="initData", min_length=1)

    model_config = ConfigDict(populate_by_name=True)


class TelegramWebAppUser(BaseModel):
    id: int = Field(gt=0)
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    language_code: str | None = Field(default=None, max_length=16)
    is_premium: bool | None = None
    allows_write_to_pm: bool | None = None
    photo_url: str | None = Field(default=None, max_length=2048)


class ValidatedTelegramInitData(BaseModel):
    """Internal DTO produced only after initData signature validation."""

    auth_date: datetime
    hash: str
    signature: str | None = None
    query_id: str | None = None
    user: TelegramWebAppUser
    start_param: str | None = None
    chat_instance: str | None = None
    chat_type: str | None = None


class TelegramAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False
