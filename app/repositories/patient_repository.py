from uuid import UUID
from datetime import date, datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.db.models import Patient


def utcnow():
    return datetime.now(timezone.utc)


class PatientRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, patient_data: dict) -> Patient:
        patient = Patient(
            patient_id=patient_data.get("patient_id"),
            first_name=patient_data["first_name"],
            last_name=patient_data["last_name"],
            date_of_birth=patient_data["date_of_birth"],
            sex=patient_data["sex"],
            phone_number=patient_data["phone_number"],
            email=patient_data.get("email"),
            address_line_1=patient_data["address_line_1"],
            address_line_2=patient_data.get("address_line_2"),
            city=patient_data["city"],
            state=patient_data["state"],
            zip_code=patient_data["zip_code"],
            insurance_provider=patient_data.get("insurance_provider"),
            insurance_member_id=patient_data.get("insurance_member_id"),
            preferred_language=patient_data.get("preferred_language", "English"),
            emergency_contact_name=patient_data.get("emergency_contact_name"),
            emergency_contact_phone=patient_data.get("emergency_contact_phone"),
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        self.session.add(patient)
        self.session.commit()
        self.session.refresh(patient)
        return patient

    def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        return self.session.query(Patient).filter(
            Patient.patient_id == patient_id,
            Patient.deleted_at.is_(None)
        ).first()

    def get_all(
        self,
        last_name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        phone_number: Optional[str] = None
    ) -> List[Patient]:
        query = self.session.query(Patient).filter(Patient.deleted_at.is_(None))
        
        if last_name:
            query = query.filter(Patient.last_name.ilike(f"%{last_name}%"))
        if date_of_birth:
            query = query.filter(Patient.date_of_birth == date_of_birth)
        if phone_number:
            query = query.filter(Patient.phone_number == phone_number)
        
        return query.order_by(Patient.created_at.desc()).all()

    def update(self, patient_id: UUID, update_data: dict) -> Optional[Patient]:
        patient = self.get_by_id(patient_id)
        if not patient:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(patient, key):
                setattr(patient, key, value)
        
        patient.updated_at = utcnow()
        self.session.commit()
        self.session.refresh(patient)
        return patient

    def soft_delete(self, patient_id: UUID) -> Optional[Patient]:
        patient = self.get_by_id(patient_id)
        if not patient:
            return None
        
        patient.deleted_at = utcnow()
        self.session.commit()
        self.session.refresh(patient)
        return patient