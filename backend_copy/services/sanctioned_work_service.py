from sqlalchemy.orm import Session
from models import WorkEntry, Station
from schemas import WorkEntryCreate
from fastapi import HTTPException
import json

def create_work(db: Session, data: WorkEntryCreate):
    stations = db.query(Station).filter(Station.station_code.in_(data.station_codes)).all()
    if len(stations) != len(data.station_codes):
        raise HTTPException(status_code=400, detail="Invalid station codes provided.")

    remarks = data.remarks.dict() if data.remarks else {}
    work = WorkEntry(
        **data.dict(exclude={"station_codes", "remarks"}),
        remarks_engineering=json.dumps(remarks.get("engineering")),
        remarks_electrical_g=json.dumps(remarks.get("electrical_g")),
        remarks_electrical_trd=json.dumps(remarks.get("electrical_trd")),
        remarks_snt=json.dumps(remarks.get("snt"))
    )
    work.stations = stations
    db.add(work)
    db.commit()
    db.refresh(work)
    return work

def get_all_works(db: Session):
    return db.query(WorkEntry).all()

def get_work(db: Session, work_id: int):
    work = db.query(WorkEntry).filter(WorkEntry.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work entry not found")
    return work

def update_work(db: Session, work_id: int, data: WorkEntryCreate):
    work = get_work(db, work_id)
    for field, value in data.dict(exclude={"station_codes", "remarks"}).items():
        setattr(work, field, value)

    work.stations = db.query(Station).filter(Station.station_code.in_(data.station_codes)).all()

    if data.remarks:
        work.remarks_engineering = json.dumps(data.remarks.engineering.dict()) if data.remarks.engineering else None
        work.remarks_electrical_g = json.dumps(data.remarks.electrical_g.dict()) if data.remarks.electrical_g else None
        work.remarks_electrical_trd = json.dumps(data.remarks.electrical_trd.dict()) if data.remarks.electrical_trd else None
        work.remarks_snt = json.dumps(data.remarks.snt.dict()) if data.remarks.snt else None

    db.commit()
    db.refresh(work)
    return work

def delete_work(db: Session, work_id: int):
    work = get_work(db, work_id)
    db.delete(work)
    db.commit()