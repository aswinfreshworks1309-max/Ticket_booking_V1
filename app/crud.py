from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
import base64

# --- Users ---
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email, phone=user.phone, password=user.password)
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter_by(id=user_id).first()

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = db.query(models.User).filter_by(id=user_id).first()
    if not db_user:
        return None
    db_user.name = user.name
    db_user.email = user.email
    db_user.phone = user.phone
    if user.password:
        db_user.password = user.password
    db.commit(); db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter_by(id=user_id).first()
    if db_user:
        db.delete(db_user); db.commit()
        return True
    return False

# --- Buses ---
def create_bus(db: Session, bus: schemas.BusCreate):
    db_bus = models.Bus(**bus.model_dump())
    db.add(db_bus); db.commit(); db.refresh(db_bus)
    return db_bus

def get_buses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bus).offset(skip).limit(limit).all()

def get_bus(db: Session, bus_id: int):
    return db.query(models.Bus).filter_by(id=bus_id).first()

def update_bus(db: Session, bus_id: int, bus: schemas.BusCreate):
    db_bus = db.query(models.Bus).filter_by(id=bus_id).first()
    if not db_bus:
        return None
    for key, value in bus.model_dump().items():
        setattr(db_bus, key, value)
    db.commit(); db.refresh(db_bus)
    return db_bus

def delete_bus(db: Session, bus_id: int):
    db_bus = db.query(models.Bus).filter_by(id=bus_id).first()
    if db_bus:
        db.delete(db_bus); db.commit()
        return True
    return False

# --- Schedules ---
def create_schedule(db: Session, schedule: schemas.ScheduleCreate):
    db_s = models.Schedule(**schedule.model_dump())
    db.add(db_s); db.commit(); db.refresh(db_s)
    return db_s

def get_schedules(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Schedule).offset(skip).limit(limit).all()

def get_schedule(db: Session, schedule_id: int):
    return db.query(models.Schedule).filter_by(id=schedule_id).first()

def get_schedules_by_route(db: Session, source: str, destination: str, travel_date):
    # join bus and schedules
    return db.query(models.Schedule).join(models.Bus).filter(
        models.Bus.source_stop == source,
        models.Bus.destination_stop == destination,
        models.Schedule.travel_date == travel_date,
        models.Schedule.status == "active"
    ).all()

def update_schedule(db: Session, schedule_id: int, schedule: schemas.ScheduleCreate):
    db_schedule = db.query(models.Schedule).filter_by(id=schedule_id).first()
    if not db_schedule:
        return None
    for key, value in schedule.model_dump().items():
        setattr(db_schedule, key, value)
    db.commit(); db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: int):
    db_schedule = db.query(models.Schedule).filter_by(id=schedule_id).first()
    if db_schedule:
        db.delete(db_schedule); db.commit()
        return True
    return False

# --- Seats ---
def generate_seats_for_schedule(db: Session, schedule_id: int, total_seats: int):
    created = []
    for i in range(1, total_seats+1):
        seat = models.Seat(schedule_id=schedule_id, seat_number=i, is_available=True)
        db.add(seat); created.append(seat)
    db.commit()
    for s in created: db.refresh(s)
    return created

def get_available_seats(db: Session, schedule_id: int):
    return db.query(models.Seat).filter_by(schedule_id=schedule_id, is_available=True).all()

def get_seat(db: Session, seat_id: int):
    return db.query(models.Seat).filter_by(id=seat_id).first()

def update_seat(db: Session, seat_id: int, is_available: bool):
    db_seat = db.query(models.Seat).filter_by(id=seat_id).first()
    if not db_seat:
        return None
    db_seat.is_available = is_available
    db.commit(); db.refresh(db_seat)
    return db_seat

def delete_seat(db: Session, seat_id: int):
    db_seat = db.query(models.Seat).filter_by(id=seat_id).first()
    if db_seat:
        db.delete(db_seat); db.commit()
        return True
    return False

# --- Booking & seat locking ---
def create_booking(db: Session, booking_in: schemas.BookingCreate):
    # calculate fare from schedule
    schedule = db.query(models.Schedule).filter_by(id=booking_in.schedule_id).first()
    if not schedule:
        raise ValueError("Schedule not found")
    # check all seat availability
    seats = db.query(models.Seat).filter(models.Seat.id.in_(booking_in.seat_ids)).with_for_update().all()
    if len(seats) != len(booking_in.seat_ids):
        raise ValueError("Some seats not found")
    for s in seats:
        if not s.is_available:
            raise ValueError(f"Seat {s.seat_number} is already booked")

    # mark seats booked
    for s in seats:
        s.is_available = False
        db.add(s)

    total_fare = schedule.fare * len(seats)
    qr_string = f"LOCOTRANZ-{booking_in.schedule_id}-{int(datetime.utcnow().timestamp())}"
    qr_code = base64.b64encode(qr_string.encode()).decode()

    db_booking = models.Booking(
        user_id=booking_in.user_id,
        schedule_id=booking_in.schedule_id,
        passenger_name=booking_in.passenger_name,
        passenger_phone=booking_in.passenger_phone,
        total_fare=total_fare,
        booking_status="CONFIRMED",
        qr_code=qr_code,
        created_at=str(datetime.utcnow())
    )
    db.add(db_booking); db.flush()  # flush to get id

    # create booking seats
    for s in seats:
        bs = models.BookingSeat(booking_id=db_booking.id, seat_id=s.id)
        db.add(bs)

    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).offset(skip).limit(limit).all()

def get_booking(db: Session, booking_id: int):
    return db.query(models.Booking).filter_by(id=booking_id).first()

def update_booking_status(db: Session, booking_id: int, status: str):
    db_booking = db.query(models.Booking).filter_by(id=booking_id).first()
    if not db_booking:
        return None
    db_booking.booking_status = status
    db.commit(); db.refresh(db_booking)
    return db_booking

def delete_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter_by(id=booking_id).first()
    if db_booking:
        # Release seats back to available
        for bs in db_booking.seats:
            seat = db.query(models.Seat).filter_by(id=bs.seat_id).first()
            if seat:
                seat.is_available = True
                db.add(seat)
        db.delete(db_booking); db.commit()
        return True
    return False

# --- Payments ---
def create_payment(db: Session, payment_in: schemas.PaymentCreate):
    booking = db.query(models.Booking).filter_by(id=payment_in.booking_id).first()
    if not booking:
        raise ValueError("Booking not found")
    pay = models.Payment(
        booking_id=payment_in.booking_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        status="SUCCESS",
        transaction_id=f"TXN-{int(datetime.utcnow().timestamp())}"
    )
    db.add(pay); db.commit(); db.refresh(pay)
    return pay

def get_payments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Payment).offset(skip).limit(limit).all()

def get_payment(db: Session, payment_id: int):
    return db.query(models.Payment).filter_by(id=payment_id).first()

def update_payment_status(db: Session, payment_id: int, status: str):
    db_payment = db.query(models.Payment).filter_by(id=payment_id).first()
    if not db_payment:
        return None
    db_payment.status = status
    db.commit(); db.refresh(db_payment)
    return db_payment

def delete_payment(db: Session, payment_id: int):
    db_payment = db.query(models.Payment).filter_by(id=payment_id).first()
    if db_payment:
        db.delete(db_payment); db.commit()
        return True
    return False
