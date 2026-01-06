from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import WorkEntryCreate, WorkEntryOut
from typing import List
from services import sanctioned_work_service as svc

router = APIRouter(prefix="/sanctioned-works", tags=["Sanctioned Works"])

@router.post("/", response_model=WorkEntryOut)
def create(entry: WorkEntryCreate, db: Session = Depends(get_db)):
    return svc.create_work(db, entry)

@router.get("/", response_model=List[WorkEntryOut])
def list_all(db: Session = Depends(get_db)):
    return svc.get_all_works(db)

@router.get("/{work_id}", response_model=WorkEntryOut)
def get_one(work_id: int, db: Session = Depends(get_db)):
    return svc.get_work(db, work_id)

@router.put("/{work_id}", response_model=WorkEntryOut)
def update(work_id: int, entry: WorkEntryCreate, db: Session = Depends(get_db)):
    return svc.update_work(db, work_id, entry)

@router.delete("/{work_id}")
def delete(work_id: int, db: Session = Depends(get_db)):
    svc.delete_work(db, work_id)
    return {"detail": "Deleted"}