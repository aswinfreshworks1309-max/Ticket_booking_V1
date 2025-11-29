from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, time

# USERS
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: Optional[str] = "user"
    class Config:
        from_attributes = True

# BUSES
class BusBase(BaseModel):
    bus_number: str
    operator_name: str
    bus_type: str
    source_stop: str
    destination_stop: str
    total_seats: int

class BusCreate(BusBase): pass
class BusResponse(BusBase):
    id: int
    class Config:
        from_attributes = True

# SCHEDULES
class ScheduleBase(BaseModel):
    bus_id: int
    travel_date: date
    departure_time: time
    arrival_time: time
    fare: float = 0.0
    status: str = "active"

class ScheduleCreate(ScheduleBase): pass
class ScheduleResponse(ScheduleBase):
    id: int
    class Config:
        from_attributes = True

# SEATS
class SeatBase(BaseModel):
    seat_number: int
    is_available: bool = True

class SeatCreate(SeatBase):
    schedule_id: int

class SeatResponse(SeatBase):
    id: int
    schedule_id: int
    class Config:
        from_attributes = True

# BOOKING SEAT
class BookingSeatResponse(BaseModel):
    id: int
    seat_id: int
    seat_number: int
    class Config:
        from_attributes = True

# BOOKINGS
class BookingBase(BaseModel):
    passenger_name: str
    passenger_phone: str

class BookingCreate(BookingBase):
    user_id: Optional[int] = None
    schedule_id: int
    seat_ids: List[int]  # chosen seat ids

class BookingResponse(BookingBase):
    id: int
    user_id: Optional[int]
    schedule_id: int
    total_fare: float
    booking_status: str
    seats: List[BookingSeatResponse] = []
    qr_code: Optional[str] = None
    class Config:
        from_attributes = True

# PAYMENTS
class PaymentBase(BaseModel):
    amount: float
    payment_method: str

class PaymentCreate(PaymentBase):
    booking_id: int

class PaymentResponse(PaymentBase):
    id: int
    booking_id: int
    status: str
    transaction_id: Optional[str] = None
    class Config:
        from_attributes = True
