# services/earning_service.py

import re
import logging
from typing import Any, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

import models, schemas
from utils import get_google_sheet, parse_date, safe_float

logger = logging.getLogger(__name__)


class EarningService:

    # ───────────────── CRUD ─────────────────

    @staticmethod
    def get_earning(db: Session, earning_id: int):
        earning = db.query(models.Earning)\
            .filter(models.Earning.earning_id == earning_id)\
            .first()
        if not earning:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Earning not found")
        return earning

    @staticmethod
    def list_earnings(db: Session):
        return db.query(models.Earning).all()

    @staticmethod
    def create_earning(db: Session, earning: schemas.EarningCreate):
        db_earning = models.Earning(**earning.dict())
        db.add(db_earning)
        db.commit()
        db.refresh(db_earning)
        return db_earning

    @staticmethod
    def update_earning(db: Session, earning_id: int, earning: schemas.EarningCreate):
        db_earning = EarningService.get_earning(db, earning_id)
        for key, value in earning.dict().items():
            setattr(db_earning, key, value)
        db.commit()
        db.refresh(db_earning)
        return db_earning

    @staticmethod
    def delete_earning(db: Session, earning_id: int):
        db_earning = EarningService.get_earning(db, earning_id)
        db.delete(db_earning)
        db.commit()
        return {"detail": "Earning deleted"}

    # ───────────── Google Sheet Sync ─────────────

    @staticmethod
    def sync_earnings(sheet_id: str, db: Session):
        logger.info("🔄 Syncing Earnings from Google Sheets")

        records: List[Dict[str, Any]] = get_google_sheet(sheet_id, "Earnings")
        skipped = 0

        for rec in records:
            row = {k.strip().lower(): v for k, v in rec.items()}

            unit_no = row.get("unit no.") or row.get("unit_no")
            if not unit_no:
                skipped += 1
                continue

            # Extract station code safely
            raw_station = row.get("station") or ""
            station_code = None
            if isinstance(raw_station, str):
                m = re.match(r"([A-Z]{2,5})", raw_station.strip())
                if m:
                    station_code = m.group(1)

            ua_raw = str(row.get("u/a case", "")).lower().strip()
            ua_case = ua_raw in ("true", "1", "yes", "y")

            earning = models.Earning(
                date_of_receipt = parse_date(row.get("date of receipt")),
                unit_no         = unit_no.strip(),
                station_code    = station_code,
                pf_no           = row.get("pf no."),
                licensee_name   = row.get("name of licensee"),
                payment_head    = row.get("payment head"),
                payment_sub_head= row.get("payment sub-head"),
                period_from     = parse_date(row.get("period from")),
                period_to       = parse_date(row.get("period to")),
                amount          = safe_float(row.get("amount")),
                gst             = safe_float(row.get("gst")),
                receipt_no      = row.get("mr no/uts no/ challan no") or row.get("receipt type"),
                mr_date         = parse_date(row.get("mr date")),
                ua_case         = ua_case,
                remarks         = row.get("remarks"),
            )

            db.merge(earning)

        db.commit()
        logger.info(f"✅ Earnings synced. Skipped {skipped} rows.")
