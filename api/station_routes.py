from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
import schemas
from services.station_service import StationService
from database import get_db

router = APIRouter(prefix="/stations", tags=["Stations"])

@router.get("/", response_model=List[schemas.Station])
def list_stations(db: Session = Depends(get_db)):
    return StationService.list_stations(db)

@router.post("/", response_model=schemas.Station, status_code=status.HTTP_201_CREATED)
def create_station(station: schemas.StationCreate, db: Session = Depends(get_db)):
    return StationService.create_station(db, station)

@router.get("/{station_code}", response_model=schemas.Station)
def get_station(station_code: str, db: Session = Depends(get_db)):
    return StationService.get_station(db, station_code)

@router.put("/{station_code}", response_model=schemas.Station)
def update_station(station_code: str, station: schemas.StationCreate, db: Session = Depends(get_db)):
    return StationService.update_station(db, station_code, station)

@router.delete("/{station_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(station_code: str, db: Session = Depends(get_db)):
    StationService.delete_station(db, station_code)
    return

# 🆕 Sync stations from Google Sheet
@router.post("/sync", status_code=status.HTTP_200_OK)
def sync_stations(sheet_id: str, db: Session = Depends(get_db)):
    StationService.sync_stations(sheet_id, db)
    return {"detail": "Stations synced successfully"}

@router.get("/top‐footfall", response_model=List[schemas.Station])
def top_footfall(limit: int = 10, db: Session = Depends(get_db)):
    return StationService.top_stations_by_footfall(db, limit)

@router.get("/by‐division", response_model=List[schemas.DivisionSummary])
def by_division(db: Session = Depends(get_db)):
    return StationService.summary_by_division(db)