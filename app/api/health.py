from pydantic import BaseModel
from fastapi import APIRouter


class HealthResponse(BaseModel):
    status: str = "ok"


class HealthEnvelope(BaseModel):
    data: HealthResponse
    error: None = None


router = APIRouter()


@router.get("/health", response_model=HealthEnvelope)
async def health_check() -> HealthEnvelope:
    return HealthEnvelope(data=HealthResponse())