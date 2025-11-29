from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.post("/", response_model=schemas.ScheduleResponse)
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    # ensure bus exists
    bus = db.query(models.Bus).filter_by(id=schedule.bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    s = crud.create_schedule(db, schedule)
    return s

@router.get("/", response_model=list[schemas.ScheduleResponse])
def list_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_schedules(db, skip=skip, limit=limit)

@router.get("/{schedule_id}", response_model=schemas.ScheduleResponse)
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = crud.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.get("/search", response_model=list[schemas.ScheduleResponse])
def search_schedules(source: str, destination: str, travel_date: str, db: Session = Depends(get_db)):
    # travel_date expected as YYYY-MM-DD string
    from datetime import datetime
    try:
        d = datetime.strptime(travel_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (YYYY-MM-DD)")
    results = crud.get_schedules_by_route(db, source, destination, d)
    return results

@router.put("/{schedule_id}", response_model=schemas.ScheduleResponse)
def update_schedule(schedule_id: int, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    updated_schedule = crud.update_schedule(db, schedule_id, schedule)
    if not updated_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated_schedule

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    success = crud.delete_schedule(db, schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted successfully"}
