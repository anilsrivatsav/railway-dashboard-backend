import logging
import re
from typing import Any, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta

import models, schemas
from utils import get_google_sheet, parse_date, safe_float

logger = logging.getLogger(__name__)


class UnitService:

    # ───────────────────────────── CRUD ─────────────────────────────

    @staticmethod
    def get_unit(db: Session, unit_no: str):
        unit = (
            db.query(models.Unit)
              .filter(models.Unit.unit_no == unit_no)
              .first()
        )
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        return unit

    @staticmethod
    def list_units(db: Session):
        return db.query(models.Unit).order_by(models.Unit.unit_no).all()

    @staticmethod
    def create_unit(db: Session, unit: schemas.UnitCreate):
        db_unit = models.Unit(**unit.dict())
        db.add(db_unit)
        db.commit()
        db.refresh(db_unit)
        return db_unit

    @staticmethod
    def update_unit(db: Session, unit_no: str, unit: schemas.UnitCreate):
        db_unit = UnitService.get_unit(db, unit_no)
        for key, value in unit.dict().items():
            setattr(db_unit, key, value)
        db.commit()
        db.refresh(db_unit)
        return db_unit

    @staticmethod
    def delete_unit(db: Session, unit_no: str):
        db_unit = UnitService.get_unit(db, unit_no)
        db.delete(db_unit)
        db.commit()
        return {"detail": "Unit deleted"}

    # ───────────────────────────── GOOGLE SHEET SYNC ─────────────────────────────

    @staticmethod
    def sync_units(sheet_id: str, db: Session):
        """
        Sync commercial units from Google Sheets.
        Fully cleans:
        - station codes
        - license fee
        - dates
        - allotment types
        - PF numbers
        """

        logger.info("🔄 Syncing Units from Google Sheets…")

        records: List[Dict[str, Any]] = get_google_sheet(sheet_id, "Units")

        skipped = 0
        updated = 0

        for rec in records:
            row = {k.strip().lower(): v for k, v in rec.items()}

            unit_no = row.get("unit no.") or row.get("unit_no")
            if not unit_no:
                skipped += 1
                continue

            # -------- Station Code Cleaning --------
            raw_station = row.get("station") or ""
            station_code = None
            if isinstance(raw_station, str):
                m = re.match(r"([A-Z]{2,5})", raw_station.strip())
                if m:
                    station_code = m.group(1)

            # -------- Money --------
            license_fee = safe_float(row.get("license fee"))

            # -------- Dates --------
            contract_from = parse_date(row.get("contract from"))
            contract_to = parse_date(row.get("contract to"))
            paid_upto = parse_date(row.get("license paid upto"))

            unit = models.Unit(
                unit_no           = unit_no.strip(),
                type_of_unit      = row.get("type of unit"),
                station_code      = station_code,
                station_category  = row.get("station category"),
                pf_no             = row.get("pf no"),
                pegged_location   = row.get("pegged location"),
                reservation_cat   = row.get("reservation category"),
                type_of_allotment = row.get("type of allotment"),
                licensee_name     = row.get("name of licensee"),
                license_fee       = license_fee,
                contract_from     = contract_from,
                contract_to       = contract_to,
                license_paid_upto = paid_upto,
                unit_status       = row.get("unit status"),
            )

            db.merge(unit)
            updated += 1

        db.commit()
        logger.info(f"✅ Units synced. Updated: {updated}, Skipped: {skipped}")

    # ───────────────────────────── ANALYTICS ─────────────────────────────

    @staticmethod
    def units_unpaid_today(db: Session):
        today = date.today()
        return (
            db.query(models.Unit)
              .filter(models.Unit.license_paid_upto < today)
              .order_by(models.Unit.license_paid_upto)
              .all()
        )

    @staticmethod
    def units_unpaid_this_month(db: Session):
        today = date.today()
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        last_day = next_month - timedelta(days=1)
        return (
            db.query(models.Unit)
              .filter(models.Unit.license_paid_upto < last_day)
              .order_by(models.Unit.license_paid_upto)
              .all()
        )

    @staticmethod
    def units_unpaid_this_year(db: Session):
        today = date.today()
        end_year = date(today.year, 12, 31)
        return (
            db.query(models.Unit)
              .filter(models.Unit.license_paid_upto < end_year)
              .order_by(models.Unit.license_paid_upto)
              .all()
        )

    @staticmethod
    def units_due_soon(db: Session, days_ahead: int = 30):
        today = date.today()
        cutoff = today + timedelta(days=days_ahead)
        return (
            db.query(models.Unit)
              .filter(models.Unit.license_paid_upto.between(today, cutoff))
              .order_by(models.Unit.license_paid_upto)
              .all()
        )
