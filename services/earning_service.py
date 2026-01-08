import logging
from typing import Any, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from utils import get_google_sheet, parse_date, safe_float

logger = logging.getLogger(__name__)


class EarningService:

    # ───────────────────────────── CRUD ─────────────────────────────

    @staticmethod
    def get_earning(db: Session, earning_id: int):
        earning = (
            db.query(models.Earning)
              .filter(models.Earning.earning_id == earning_id)
              .first()
        )
        if not earning:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Earning not found"
            )
        return earning

    @staticmethod
    def list_earnings(db: Session):
        return (
            db.query(models.Earning)
              .order_by(models.Earning.date_of_receipt.desc())
              .all()
        )

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

    # ───────────────────────────── GOOGLE SHEET SYNC ─────────────────────────────

    @staticmethod
    def sync_earnings(sheet_id: str, db: Session):
        """
        Sync earnings from Google Sheets.
        Handles:
        - ₹ and comma money
        - date parsing
        - receipt numbers
        - UA cases
        - null safety
        """

        logger.info("🔄 Syncing Earnings from Google Sheets…")

        records: List[Dict[str, Any]] = get_google_sheet(sheet_id, "Earnings")

        skipped = 0
        updated = 0

        for rec in records:
            row = {k.strip().lower(): v for k, v in rec.items()}

            unit_no = row.get("unit no.") or row.get("unit_no")
            if not unit_no:
                skipped += 1
                continue

            earning = models.Earning(
                date_of_receipt = parse_date(row.get("date of receipt")),
                unit_no         = unit_no,
                station_code    = row.get("station"),
                pf_no           = row.get("pf no.") or row.get("pf no"),
                licensee_name   = row.get("name of licensee"),
                payment_head    = row.get("payment head"),
                payment_sub_head= row.get("payment sub-head"),
                period_from     = parse_date(row.get("period from")),
                period_to       = parse_date(row.get("period to")),
                amount          = safe_float(row.get("amount")),
                gst             = safe_float(row.get("gst")),
                receipt_no      = row.get("mr no/uts no/ challan no") or row.get("receipt no"),
                mr_date         = parse_date(row.get("mr date")),
                ua_case         = str(row.get("u/a case")).strip().lower() in ("true", "1", "yes"),
                remarks         = row.get("remarks"),
            )

            db.merge(earning)
            updated += 1

        db.commit()
        logger.info(f"✅ Earnings synced. Updated: {updated}, Skipped: {skipped}")
