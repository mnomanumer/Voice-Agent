from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import get_logger
from app.api.health import router as health_router
from app.api.patients import router as patients_router
from app.web.dashboard import router as dashboard_router
from app.db.database import init_db


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")
    init_db()
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="CareCloud Voice AI Patient Registration",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    error_detail = {
        "code": "VALIDATION_ERROR",
        "message": "; ".join(errors)
    }
    logger.warning(f"Validation error: {error_detail['message']}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"data": None, "error": error_detail}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    status_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "PATIENT_NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
    }
    error_code = status_codes.get(exc.status_code, "HTTP_ERROR")
    error_detail = {
        "code": error_code,
        "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    }
    logger.warning(f"HTTP error {exc.status_code}: {error_detail['message']}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": error_detail}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal error: {type(exc).__name__}: {exc}", exc_info=True)
    error_detail = {
        "code": "INTERNAL_ERROR",
        "message": "An unexpected error occurred."
    }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"data": None, "error": error_detail}
    )


app.include_router(health_router, prefix="")
app.include_router(patients_router)
app.include_router(dashboard_router)