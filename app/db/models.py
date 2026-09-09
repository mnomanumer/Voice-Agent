import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Date, DateTime, Index, text
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(String(20), nullable=False)
    phone_number = Column(String(10), nullable=False)
    email = Column(String(255), nullable=True)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    insurance_provider = Column(String(255), nullable=True)
    insurance_member_id = Column(String(100), nullable=True)
    preferred_language = Column(String(100), default="English", nullable=False)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(10), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_patients_last_name", "last_name"),
        Index("ix_patients_date_of_birth", "date_of_birth"),
        Index("ix_patients_phone_number", "phone_number"),
    )