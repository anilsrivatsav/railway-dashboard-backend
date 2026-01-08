import re
import logging
from typing import Any, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from utils import get_google_sheet, safe_int, parse_bool

logger = logging.getLogger(__name__)


class StationService:

    # ───────────────────────────── CRUD ─────────────────────────────

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
        return (
            db.query(models.Station)
              .order_by(models.Station.station_name)
              .all()
        )

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

    # ───────────────────────────── GOOGLE SHEET SYNC ─────────────────────────────

    @staticmethod
    def sync_stations(sheet_id: str, db: Session):
       """
       Sync station master from Google Sheets.
       Correctly reads Passenger Footfall, ranges, platforms and booleans.
       """
   
       logger.info("🔄 Syncing Stations from Google Sheets…")
   
       records: List[Dict[str, Any]] = get_google_sheet(sheet_id, "Stations")
   
       skipped = 0
       updated = 0
   
       for rec in records:
           # Normalize headers
           row = {k.strip().lower(): v for k, v in rec.items()}
   
           station_code = row.get("station code")
           station_name = row.get("station name")
   
           if not station_code or not station_name:
               skipped += 1
               continue
   
           # ─── PLATFORM COUNT ─────────────────────────────
           raw_platforms = row.get("number of platforms") or row.get("platforms") or ""
           platform_count = safe_int(raw_platforms)
   
           # ─── 🔥 THIS IS THE REAL FOOTFALL ───────────────
           passenger_footfall = safe_int(row.get("passenger footfall"))
   
           station = models.Station(
               station_code    = station_code.strip(),
               station_name    = station_name.strip(),
               division        = row.get("division"),
               zone            = row.get("zone"),
               section         = row.get("section"),
               cmi             = row.get("cmi"),
               den             = row.get("den"),
               sr_den          = row.get("sr.den") or row.get("sr den"),
               categorisation  = row.get("categorisation"),
               earnings_range  = row.get("earnings range"),
               passenger_range = row.get("passenger range"),
   
               # ✅ FIXED: now reads real number like 73451
               footfall        = passenger_footfall,
   
               platforms       = row.get("platforms"),
               platform_count  = platform_count,
               platform_type   = row.get("platform type"),
               parking         = parse_bool(row.get("parking")),
               pay_and_use     = parse_bool(row.get("pay & use")),
           )
   
           db.merge(station)
           updated += 1
   
       db.commit()
       logger.info(f"✅ Stations sync complete. Updated {updated}, Skipped {skipped}")
