from uuid import UUID
from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.patient_service import PatientService
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    APIResponse,
    ErrorDetail,
)


router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=APIResponse[PatientResponse], status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
) -> APIResponse[PatientResponse]:
    service = PatientService(db)
    result = service.create_patient(patient)
    return APIResponse(data=result)


@router.get("", response_model=APIResponse[List[PatientResponse]])
async def list_patients(
    last_name: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    phone_number: Optional[str] = None,
    db: Session = Depends(get_db),
) -> APIResponse[List[PatientResponse]]:
    service = PatientService(db)
    patients = service.list_patients(last_name, date_of_birth, phone_number)
    return APIResponse(data=patients)


@router.get("/{patient_id}", response_model=APIResponse[PatientResponse])
async def get_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
) -> APIResponse[PatientResponse]:
    service = PatientService(db)
    patient = service.get_patient(patient_id)
    return APIResponse(data=patient)


@router.put("/{patient_id}", response_model=APIResponse[PatientResponse])
async def update_patient(
    patient_id: UUID,
    patient: PatientUpdate,
    db: Session = Depends(get_db),
) -> APIResponse[PatientResponse]:
    service = PatientService(db)
    result = service.update_patient(patient_id, patient)
    return APIResponse(data=result)


@router.delete("/{patient_id}", response_model=APIResponse[PatientResponse])
async def delete_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
) -> APIResponse[PatientResponse]:
    service = PatientService(db)
    result = service.delete_patient(patient_id)
    return APIResponse(data=result)