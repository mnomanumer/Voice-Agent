from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
)
from app.core.logging import get_logger


logger = get_logger(__name__)


class PatientService:
    def __init__(self, session: Session):
        self.repository = PatientRepository(session)

    def create_patient(self, data: PatientCreate) -> PatientResponse:
        patient = self.repository.create(data.model_dump())
        logger.info(
            f"Patient created: patient_id={patient.patient_id} "
            f"first_name={patient.first_name} last_name={patient.last_name}"
        )
        return PatientResponse.model_validate(patient)

    def get_patient(self, patient_id: UUID) -> PatientResponse:
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient was not found."
            )
        return PatientResponse.model_validate(patient)

    def list_patients(
        self,
        last_name: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> List[PatientResponse]:
        patients = self.repository.get_all(last_name, date_of_birth, phone_number)
        return [PatientResponse.model_validate(p) for p in patients]

    def update_patient(self, patient_id: UUID, data: PatientUpdate) -> PatientResponse:
        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        patient = self.repository.update(patient_id, update_dict)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient was not found."
            )
        return PatientResponse.model_validate(patient)

    def delete_patient(self, patient_id: UUID) -> PatientResponse:
        patient = self.repository.soft_delete(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient was not found."
            )
        return PatientResponse.model_validate(patient)