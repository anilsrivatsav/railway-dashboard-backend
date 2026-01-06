from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
import schemas
from services.earning_service import EarningService
from database import get_db
from datetime import date
router = APIRouter(prefix="/earnings", tags=["Earnings"])

@router.get("/", response_model=List[schemas.Earning])
def list_earnings(db: Session = Depends(get_db)):
    return EarningService.list_earnings(db)

@router.post("/", response_model=schemas.Earning, status_code=status.HTTP_201_CREATED)
def create_earning(earning: schemas.EarningCreate, db: Session = Depends(get_db)):
    return EarningService.create_earning(db, earning)

@router.get("/{earning_id}", response_model=schemas.Earning)
def get_earning(earning_id: int, db: Session = Depends(get_db)):
    return EarningService.get_earning(db, earning_id)

@router.put("/{earning_id}", response_model=schemas.Earning)
def update_earning(earning_id: int, earning: schemas.EarningCreate, db: Session = Depends(get_db)):
    return EarningService.update_earning(db, earning_id, earning)

@router.delete("/{earning_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_earning(earning_id: int, db: Session = Depends(get_db)):
    EarningService.delete_earning(db, earning_id)
    return

# 🆕 Sync earnings from Google Sheet
@router.post("/sync", status_code=status.HTTP_200_OK)
def sync_earnings(sheet_id: str, db: Session = Depends(get_db)):
    EarningService.sync_earnings(sheet_id, db)
    return {"detail": "Earnings synced successfully"}


@router.get("/totals", response_model=schemas.EarningTotal)
def earnings_total(
    start: date = Query(...),
    end:   date = Query(...)
, db: Session = Depends(get_db)):
    total = EarningService.totals_over_period(db, start, end)
    return {"total": total}

@router.get("/filter", response_model=List[schemas.Earning])
def earnings_filter(
    params: schemas.EarningFilterParams = Depends(),
    db: Session = Depends(get_db)
):
    return EarningService.list_filtered(
        db,
        date_from=params.date_from,
        date_to=params.date_to,
        unit_no=params.unit_no
    )