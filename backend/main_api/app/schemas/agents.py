from datetime import date, datetime
import re

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator


AGENT_STATUSES = {"individual", "self_employed", "ip"}


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def calculate_age(birthdate: date, today: date | None = None) -> int:
    current_date = today or date.today()
    years = current_date.year - birthdate.year

    if (current_date.month, current_date.day) < (birthdate.month, birthdate.day):
        years -= 1

    return years


class AgentBase(BaseModel):
    lastname: str
    firstname: str
    middlename: str | None = None

    phone: str
    email: EmailStr

    passport_serial: str
    passport_number: str
    passport_issue_date: datetime | None = None
    passport_issuer: str
    passport_code: str

    birthdate: date | None = None

    status: str
    inn: str
    ogrnip: str
    is_verified: bool = False

    @field_validator(
        "lastname",
        "firstname",
        "passport_issuer",
        mode="before",
    )
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if cls.__name__ == "AgentRead":
            return value

        if not isinstance(value, str) or not value.strip():
            raise ValueError("Field is required")

        return value.strip()

    @field_validator("middlename", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if cls.__name__ == "AgentRead":
            return value

        if value is None:
            return None

        value = value.strip()
        return value or None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if cls.__name__ == "AgentRead":
            return value

        phone_digits = digits_only(value)

        if len(phone_digits) not in {10, 11}:
            raise ValueError("Phone must contain 10 or 11 digits")

        if len(phone_digits) == 11 and phone_digits[0] not in {"7", "8"}:
            raise ValueError("Russian phone must start with 7 or 8")

        return phone_digits

    @field_validator("passport_serial")
    @classmethod
    def validate_passport_serial(cls, value: str) -> str:
        if cls.__name__ == "AgentRead":
            return value

        value_digits = digits_only(value)

        if len(value_digits) != 4:
            raise ValueError("Passport serial must contain 4 digits")

        return value_digits

    @field_validator("passport_number")
    @classmethod
    def validate_passport_number(cls, value: str) -> str:
        if cls.__name__ == "AgentRead":
            return value

        value_digits = digits_only(value)

        if len(value_digits) != 6:
            raise ValueError("Passport number must contain 6 digits")

        return value_digits

    @field_validator("passport_code")
    @classmethod
    def validate_passport_code(cls, value: str) -> str:
        if cls.__name__ == "AgentRead":
            return value

        value_digits = digits_only(value)

        if len(value_digits) != 6:
            raise ValueError("Passport code must contain 6 digits")

        return f"{value_digits[:3]}-{value_digits[3:]}"

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if cls.__name__ == "AgentRead":
            return value

        if value not in AGENT_STATUSES:
            raise ValueError("Unknown agent status")

        return value

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, value: date | None) -> date | None:
        if cls.__name__ == "AgentRead":
            return value

        if value is None:
            raise ValueError("Birthdate is required")

        if value > date.today():
            raise ValueError("Birthdate cannot be in the future")

        age = calculate_age(value)

        if age < 18:
            raise ValueError("Agent must be at least 18 years old")

        if age > 100:
            raise ValueError("Agent age cannot be greater than 100 years")

        return value

    @field_validator("passport_issue_date")
    @classmethod
    def validate_passport_issue_date(cls, value: datetime | None) -> datetime | None:
        if cls.__name__ == "AgentRead":
            return value

        if value is None:
            raise ValueError("Passport issue date is required")

        if value.date() > date.today():
            raise ValueError("Passport issue date cannot be in the future")

        return value

    @model_validator(mode="after")
    def validate_identity_numbers(self):
        if self.__class__.__name__ == "AgentRead":
            return self

        self.inn = digits_only(self.inn)
        self.ogrnip = digits_only(self.ogrnip)

        if self.passport_issue_date and self.birthdate:
            passport_age = calculate_age(self.birthdate, self.passport_issue_date.date())

            if passport_age < 14:
                raise ValueError("Passport cannot be issued before age 14")

        if self.status in {"self_employed", "ip"} and len(self.inn) != 12:
            raise ValueError("INN for self-employed agents and IP must contain 12 digits")

        if self.status == "individual" and self.inn and len(self.inn) != 12:
            raise ValueError("INN must contain 12 digits")

        if self.status == "ip":
            if len(self.ogrnip) != 15:
                raise ValueError("OGRNIP must contain 15 digits")
        elif self.ogrnip:
            raise ValueError("OGRNIP is allowed only for IP status")

        return self


class AgentCreate(AgentBase):
    password: str

class AgentLogin(BaseModel):
    email:EmailStr
    password: str


class AgentCreateRepository(AgentBase):
    password_hash: str


class AgentUpdate(BaseModel):
    lastname: str | None = None
    firstname: str | None = None
    middlename: str | None = None

    phone: str | None = None
    email: EmailStr | None = None

    passport_serial: str | None = None
    passport_number: str | None = None
    passport_issue_date: datetime | None = None
    passport_issuer: str | None = None
    passport_code: str | None = None

    birthdate: date | None = None

    status: str | None = None
    inn: str | None = None
    ogrnip: str | None = None
    is_verified: bool | None = None


class AgentRead(AgentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
