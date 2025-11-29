from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=schemas.BookingResponse)
def create_booking(payload: schemas.BookingCreate, db: Session = Depends(get_db)):
    try:
        booking = crud.create_booking(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # convert booking to response schema
    # build seats list
    seats_resp = []
    for bs in booking.seats:
        seats_resp.append({
            "id": bs.id,
            "seat_id": bs.seat_id,
            "seat_number": bs.seat.seat_number
        })
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "schedule_id": booking.schedule_id,
        "passenger_name": booking.passenger_name,
        "passenger_phone": booking.passenger_phone,
        "total_fare": booking.total_fare,
        "booking_status": booking.booking_status,
        "seats": seats_resp,
        "qr_code": booking.qr_code
    }

@router.get("/", response_model=list[schemas.BookingResponse])
def list_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = crud.get_bookings(db, skip=skip, limit=limit)
    result = []
    for booking in bookings:
        seats_resp = []
        for bs in booking.seats:
            seats_resp.append({
                "id": bs.id,
                "seat_id": bs.seat_id,
                "seat_number": bs.seat.seat_number
            })
        result.append({
            "id": booking.id,
            "user_id": booking.user_id,
            "schedule_id": booking.schedule_id,
            "passenger_name": booking.passenger_name,
            "passenger_phone": booking.passenger_phone,
            "total_fare": booking.total_fare,
            "booking_status": booking.booking_status,
            "seats": seats_resp,
            "qr_code": booking.qr_code
        })
    return result

@router.get("/{booking_id}", response_model=schemas.BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter_by(id=booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    seats_resp = []
    for bs in booking.seats:
        seats_resp.append({
            "id": bs.id,
            "seat_id": bs.seat_id,
            "seat_number": bs.seat.seat_number
        })
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "schedule_id": booking.schedule_id,
        "passenger_name": booking.passenger_name,
        "passenger_phone": booking.passenger_phone,
        "total_fare": booking.total_fare,
        "booking_status": booking.booking_status,
        "seats": seats_resp,
        "qr_code": booking.qr_code
    }

@router.put("/{booking_id}", response_model=schemas.BookingResponse)
def update_booking(booking_id: int, status: str, db: Session = Depends(get_db)):
    booking = crud.update_booking_status(db, booking_id, status)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    seats_resp = []
    for bs in booking.seats:
        seats_resp.append({
            "id": bs.id,
            "seat_id": bs.seat_id,
            "seat_number": bs.seat.seat_number
        })
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "schedule_id": booking.schedule_id,
        "passenger_name": booking.passenger_name,
        "passenger_phone": booking.passenger_phone,
        "total_fare": booking.total_fare,
        "booking_status": booking.booking_status,
        "seats": seats_resp,
        "qr_code": booking.qr_code
    }

@router.delete("/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    success = crud.delete_booking(db, booking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking deleted successfully"}
