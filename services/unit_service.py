# services/unit_service.py

import logging
from typing import Any, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta

import models, schemas
from utils import get_google_sheet, parse_date, safe_float

logger = logging.getLogger(__name__)

class UnitService:
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
        return db.query(models.Unit).all()

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

    @staticmethod
    def sync_units(sheet_id: str, db: Session):
        """
        Pull the 'Units' tab (using the passed sheet_id if you ever extend get_google_sheet),
        skip rows missing UNIT NO., upsert the rest.
        """
        logger.info(f"🔄 Syncing Units from sheet {sheet_id}…")
        records: List[Dict[str, Any]] = get_google_sheet(sheet_id, 'Units')
        skipped = 0


        for rec in records:
            unit_no = rec.get('UNIT NO.') or rec.get('unit_no')
            if not unit_no:
                skipped += 1
                logger.warning(f"Skipping unit record with missing UNIT NO.: {rec}")
                continue

            db_unit = models.Unit(
                unit_no            = unit_no,
                type_of_unit       = rec.get('TYPE OF UNIT'),
                station_code       = rec.get('STATION'),
                station_category   = rec.get('STATION CATEGORY'),
                pegged_location    = rec.get('PEGGED LOCATION'),
                reservation_cat    = rec.get('RESERVATION CATEGORY'),
                type_of_allotment  = rec.get('TYPE OF ALLOTMENT'),
                licensee_name      = rec.get('NAME OF LICENSEE'),
                license_fee        = safe_float(rec.get('LICENSE FEE')),
                contract_from      = parse_date(rec.get('CONTRACT from')),
                contract_to        = parse_date(rec.get('CONTRACT to')),
                license_paid_upto  = parse_date(rec.get('LICENSE PAID UPTO')),
                unit_status        = rec.get('UNIT STATUS'),
            )
            db.merge(db_unit)

        db.commit()
        logger.info(f"✅ Units sync complete. Skipped {skipped} records.")

    # ─── Analytics / Reports ────────────────────────────────────────────────

    @staticmethod
    def units_unpaid_today(db: Session):
        """All units whose paid-up-to date is before today."""
        today = date.today()
        return (
            db.query(models.Unit)
              .filter(models.Unit.license_paid_upto < today)
              .order_by(models.Unit.license_paid_upto)
              .all()
        )

    @staticmethod
    def units_unpaid_this_month(db: Session):
        """Units whose license_paid_upto < last day of current month."""
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
        """Units whose license_paid_upto < Dec 31 of current year."""
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
        """
        Units whose license_paid_upto is within the next `days_ahead` days.
        """
        today = date.today()
        cutoff = today + timedelta(days=days_ahead)
        return (
            db.query(models.Unit)
              .filter(models.Unit.license_paid_upto.between(today, cutoff))
              .order_by(models.Unit.license_paid_upto)
              .all()
        )