from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
import schemas
from services.unit_service import UnitService
from database import get_db

router = APIRouter(prefix="/units", tags=["Units"])

@router.get("/", response_model=List[schemas.Unit])
def list_units(db: Session = Depends(get_db)):
    return UnitService.list_units(db)

@router.post("/", response_model=schemas.Unit, status_code=status.HTTP_201_CREATED)
def create_unit(unit: schemas.UnitCreate, db: Session = Depends(get_db)):
    return UnitService.create_unit(db, unit)

@router.get("/{unit_no}", response_model=schemas.Unit)
def get_unit(unit_no: str, db: Session = Depends(get_db)):
    return UnitService.get_unit(db, unit_no)

@router.put("/{unit_no}", response_model=schemas.Unit)
def update_unit(unit_no: str, unit: schemas.UnitCreate, db: Session = Depends(get_db)):
    return UnitService.update_unit(db, unit_no, unit)

@router.delete("/{unit_no}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(unit_no: str, db: Session = Depends(get_db)):
    UnitService.delete_unit(db, unit_no)
    return

# 🆕 Sync units from Google Sheet
@router.post("/sync", status_code=status.HTTP_200_OK)
def sync_units(sheet_id: str, db: Session = Depends(get_db)):
    UnitService.sync_units(sheet_id, db)
    return {"detail": "Units synced successfully"}

@router.get("/near‐expiry", response_model=List[schemas.Unit])
def units_near_expiry(days_ahead: int = 30, db: Session = Depends(get_db)):
    return UnitService.units_near_expiry(db, days_ahead)