from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "api_base_url": settings.api_base_url}
    )