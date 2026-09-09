import re
from datetime import date, datetime
from typing import Any, Generic, Optional, TypeVar, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from pydantic.config import ConfigDict


US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "PR", "VI", "GU", "AS", "MP",
}

NAME_PATTERN = re.compile(r"^[A-Za-z\s\-']{1,50}$")
ZIP_PATTERN = re.compile(r"^\d{5}(-\d{4})?$")
PHONE_PATTERN = re.compile(r"^\d{10}$")
SEX_OPTIONS = ("Male", "Female", "Other", "Decline to Answer")


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if not PHONE_PATTERN.match(digits):
        raise ValueError("Phone number must be exactly 10 digits after normalization")
    return digits


def validate_name(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Name cannot be empty")
    if len(stripped) > 50:
        raise ValueError("Name cannot exceed 50 characters")
    if not NAME_PATTERN.match(stripped):
        raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
    return stripped


def validate_date_of_birth(value: Any) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError("Date must be in MM/DD/YYYY or YYYY-MM-DD format")
    raise ValueError("Invalid date format")


class ErrorDetail(BaseModel):
    code: str
    message: str


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Union[date, str]
    sex: str
    phone_number: str
    email: Optional[EmailStr] = None
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: str = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class PatientCreate(PatientBase):
    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_fields(cls, v: str) -> str:
        return validate_name(v)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Any) -> date:
        dob = validate_date_of_birth(v)
        if dob > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return dob

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str) -> str:
        if v not in SEX_OPTIONS:
            raise ValueError(f"Sex must be one of: {', '.join(SEX_OPTIONS)}")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)

    @field_validator("address_line_1", "city")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty")
        return stripped

    @field_validator("address_line_1", "address_line_2", "city")
    @classmethod
    def validate_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 255:
            raise ValueError("Field cannot exceed 255 characters")
        if v is not None and len(v) > 100 and v not in ("address_line_1", "address_line_2"):
            raise ValueError("City cannot exceed 100 characters")
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        upper = v.strip().upper()
        if upper not in US_STATES:
            raise ValueError("Invalid US state code")
        return upper

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: str) -> str:
        stripped = v.strip()
        if not ZIP_PATTERN.match(stripped):
            raise ValueError("ZIP code must be 5 digits or ZIP+4 format")
        return stripped

    @field_validator("insurance_member_id")
    @classmethod
    def validate_insurance_member_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.isalnum():
            raise ValueError("Insurance member ID must be alphanumeric")
        return v

    @field_validator("emergency_contact_phone")
    @classmethod
    def validate_emergency_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return normalize_phone(v)
        return v


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[Union[date, str]] = None
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_name(v)
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[Any]) -> Optional[date]:
        if v is not None:
            dob = validate_date_of_birth(v)
            if dob > date.today():
                raise ValueError("Date of birth cannot be in the future")
            return dob
        return v

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in SEX_OPTIONS:
            raise ValueError(f"Sex must be one of: {', '.join(SEX_OPTIONS)}")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return normalize_phone(v)
        return v

    @field_validator("address_line_1", "city")
    @classmethod
    def validate_non_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Field cannot be empty")
            return stripped
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            upper = v.strip().upper()
            if upper not in US_STATES:
                raise ValueError("Invalid US state code")
            return upper
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not ZIP_PATTERN.match(stripped):
                raise ValueError("ZIP code must be 5 digits or ZIP+4 format")
            return stripped
        return v

    @field_validator("insurance_member_id")
    @classmethod
    def validate_insurance_member_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.isalnum():
            raise ValueError("Insurance member ID must be alphanumeric")
        return v

    @field_validator("emergency_contact_phone")
    @classmethod
    def validate_emergency_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return normalize_phone(v)
        return v


class PatientResponse(BaseModel):
    patient_id: UUID
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone_number: str
    email: Optional[str] = None
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: str
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)