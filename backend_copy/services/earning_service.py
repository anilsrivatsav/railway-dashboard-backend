# services/earning_service.py
import logging
from typing import Any, Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from utils import get_google_sheet, parse_date, safe_float
logger = logging.getLogger(__name__)
class EarningService:
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

    @staticmethod
    def sync_earnings(sheet_id: str, db: Session) -> dict:
        """
        Fetch all rows from the 'Earnings' sheet and upsert them
        into the database, allowing date_of_receipt to be None.
        Returns a summary dict.
        """
        records: List[Dict[str, Any]] = get_google_sheet(sheet_id, 'Earnings')
        skipped = 0

        for record in records:
            # parse all dates (may return None)
            date_of_receipt = parse_date(record.get('DATE OF RECEIPT'))
            period_from     = parse_date(record.get('PERIOD from'))
            period_to       = parse_date(record.get('PERIOD to'))
            mr_date         = parse_date(record.get('MR DATE'))

            # normalize U/A CASE to bool
            ua_raw = str(record.get('U/A CASE', '')).strip().lower()
            ua_case = ua_raw in ('true', '1', 'yes')
            if not record.get('UNIT NO.') and not record.get('unit_no'):
                logger.warning(f"Skipping earnings record with missing UNIT NO.: {record}")
                continue
            unit_no = record.get('UNIT NO.') or record.get('unit_no')
            if not unit_no:
                    logger.warning(f"Skipping earnings record with missing UNIT NO.: {record}")
                    continue
            # unify receipt_no field
            receipt_no = (
                record.get('MR NO/UTS NO/ CHALLAN NO') or
                record.get('RECIEPT TYPE')
            )

            earning = models.Earning(
                date_of_receipt=date_of_receipt,
                unit_no=record.get('UNIT NO.') or record.get('UNIT NO') or record.get('unit_no'),
                station_code=record.get('STATION'),
                pf_no=record.get('PF NO.') or record.get('PF NO'),
                licensee_name=record.get('NAME OF LICENSEE'),
                payment_head=record.get('PAYMENT HEAD'),
                payment_sub_head=record.get('PAYMENT SUB-HEAD'),
                period_from=period_from,
                period_to=period_to,
                amount=safe_float(record.get('AMOUNT')),
                gst=safe_float(record.get('GST')),
                receipt_no=receipt_no,
                mr_date=mr_date,
                ua_case=ua_case,
                remarks=record.get('REMARKS', '')
            )
            db.merge(earning)

        db.commit()
        logger.info(f"✅ Earnings sync complete. Skipped {skipped} records.")