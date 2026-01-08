# services/station_service.py

import re
import logging
from typing import Any, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from utils import get_google_sheet, safe_float, parse_bool, parse_date

logger = logging.getLogger(__name__)

class StationService:
    @staticmethod
    def get_station(db: Session, station_code: str):
        station = (
            db.query(models.Station)
              .filter(models.Station.station_code == station_code)
              .first()
        )
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Station not found",
            )
        return station

    @staticmethod
    def list_stations(db: Session):
        return db.query(models.Station).all()

    @staticmethod
    def create_station(db: Session, station: schemas.StationCreate):
        db_station = models.Station(**station.dict())
        db.add(db_station)
        db.commit()
        db.refresh(db_station)
        return db_station

    @staticmethod
    def update_station(db: Session, station_code: str, station: schemas.StationCreate):
        db_station = StationService.get_station(db, station_code)
        for key, value in station.dict().items():
            setattr(db_station, key, value)
        db.commit()
        db.refresh(db_station)
        return db_station

    @staticmethod
    def delete_station(db: Session, station_code: str):
        db_station = StationService.get_station(db, station_code)
        db.delete(db_station)
        db.commit()
        return {"detail": "Station deleted"}

    @staticmethod
    
    def sync_stations(sheet_id: str, db: Session):
     """
     Pulls the 'Stations' tab from Google Sheets and upserts into DB.
     Designed specifically for Indian Railways commercial data.
     """
     logger.info("🔄 Syncing Stations from Google Sheets...")
  
     records: List[Dict[str, Any]] = get_google_sheet(sheet_id, "Stations")
     logger.info(f"📄 Fetched {len(records)} rows")
  
     skipped = 0
     updated = 0
  
     for rec in records:
         # Normalize column headers
         row = {k.strip().lower(): v for k, v in rec.items()}
  
         station_code = row.get("station code") or row.get("station_code")
         station_name = row.get("station name") or row.get("station_name")
  
         if not station_code or not station_name:
             skipped += 1
             logger.warning(f"Skipping invalid row: {row}")
             continue
  
         # --------------------------
         # PLATFORM COUNT PARSING
         # --------------------------
         raw_platforms = row.get("platforms") or row.get("number of platforms") or ""
         pc = 0
  
         if isinstance(raw_platforms, str):
             matches = re.findall(r"\d+", raw_platforms)
             if matches:
                 try:
                     pc = max(int(x) for x in matches)   # "1, 2/3" → 3
                 except:
                     pc = 0
         else:
             try:
                 pc = int(raw_platforms)
             except:
                 pc = 0
  
         station = models.Station(
             station_code    = station_code.strip(),
             station_name    = station_name.strip(),
  
             division        = row.get("division"),
             zone            = row.get("zone"),
             section         = row.get("section"),
             cmi             = row.get("cmi"),
             den             = row.get("den"),
             sr_den          = row.get("sr den"),
  
             categorisation  = row.get("categorisation"),
  
             # These are NOT numeric – keep them as business classes
             earnings_range  = row.get("earnings range"),
             passenger_range = row.get("passenger range"),
  
             # Physical infra
             platforms       = raw_platforms,
             platform_count  = pc,
             platform_type   = row.get("platform type"),
  
             # Facilities
             parking         = parse_bool(row.get("parking")),
             pay_and_use     = parse_bool(row.get("pay & use")),
         )
  
         db.merge(station)
         updated += 1
  
     db.commit()
  
     logger.info(f"✅ Station Sync Complete | Updated: {updated}, Skipped: {skipped}")
