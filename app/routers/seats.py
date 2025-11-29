from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter(prefix="/seats", tags=["seats"])

@router.post("/generate/{schedule_id}", response_model=list[schemas.SeatResponse])
def generate_seats(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(models.Schedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    # if seats exist already, return them
    existing = db.query(models.Seat).filter_by(schedule_id=schedule_id).all()
    if existing:
        return existing
    created = crud.generate_seats_for_schedule(db, schedule_id, schedule.bus.total_seats)
    return created

@router.get("/available/{schedule_id}", response_model=list[schemas.SeatResponse])
def available_seats(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(models.Schedule).filter_by(id=schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    seats = crud.get_available_seats(db, schedule_id)
    return seats

@router.get("/{seat_id}", response_model=schemas.SeatResponse)
def get_seat(seat_id: int, db: Session = Depends(get_db)):
    seat = crud.get_seat(db, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    return seat

@router.put("/{seat_id}", response_model=schemas.SeatResponse)
def update_seat(seat_id: int, is_available: bool, db: Session = Depends(get_db)):
    seat = crud.update_seat(db, seat_id, is_available)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    return seat

@router.delete("/{seat_id}")
def delete_seat(seat_id: int, db: Session = Depends(get_db)):
    success = crud.delete_seat(db, seat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Seat not found")
    return {"message": "Seat deleted successfully"}
