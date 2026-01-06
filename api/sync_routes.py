
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from services.station_service import StationService
from services.unit_service import UnitService
from services.earning_service import EarningService
from database import get_db
from utils import logger

router = APIRouter(prefix="/sync", tags=["Sync"])



@router.post("/all")
def sync_all(sheet_id: str = Query(..., description="Google Sheet ID"), db: Session = Depends(get_db)):
    """
    This will call StationService.sync_stations, UnitService.sync_units, and EarningService.sync_earnings,
    each of which now expects sheet_id as a query param rather than a JSON body.
    """
    logger.info(f"🔄 Starting sync_all with sheet_id: {sheet_id}")
    StationService.sync_stations(sheet_id, db)
    logger.info("✅ Stations sync complete")
    UnitService.sync_units(sheet_id, db)
    logger.info("✅ Units sync complete")
    EarningService.sync_earnings(sheet_id, db)
    logger.info("✅ Earnings sync complete")
    return {"detail": "All data synced successfully."}