from fastapi import APIRouter
from services.history_service import get_historical_cases

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/cases")
def historical_cases(project_name: str, customer: str):
    cases = get_historical_cases(project_name, customer, limit=2)
    return cases