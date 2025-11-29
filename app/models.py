from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, Date, Time, Text
)
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=True)  # optional for later
    role = Column(String, default="user")
    bookings = relationship("Booking", back_populates="user")

class Bus(Base):
    __tablename__ = "buses"
    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String, nullable=False)
    operator_name = Column(String, nullable=False)
    bus_type = Column(String, nullable=False)
    source_stop = Column(String, nullable=False)
    destination_stop = Column(String, nullable=False)
    total_seats = Column(Integer, nullable=False)
    schedules = relationship("Schedule", back_populates="bus")

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"))
    travel_date = Column(Date, nullable=False)
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)
    fare = Column(Float, nullable=False, default=0.0)
    status = Column(String, default="active")
    bus = relationship("Bus", back_populates="schedules")
    seats = relationship("Seat", back_populates="schedule", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="schedule")

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    seat_number = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    schedule = relationship("Schedule", back_populates="seats")
    booked_seat = relationship("BookingSeat", back_populates="seat", uselist=False)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    passenger_name = Column(String, nullable=False)
    passenger_phone = Column(String, nullable=False)
    total_fare = Column(Float, nullable=False)
    booking_status = Column(String, default="CONFIRMED")
    qr_code = Column(Text, nullable=True)
    created_at = Column(String, nullable=True)
    user = relationship("User", back_populates="bookings")
    schedule = relationship("Schedule", back_populates="bookings")
    seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False)

class BookingSeat(Base):
    __tablename__ = "booking_seats"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    seat_id = Column(Integer, ForeignKey("seats.id"))
    booking = relationship("Booking", back_populates="seats")
    seat = relationship("Seat", back_populates="booked_seat")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    transaction_id = Column(String, nullable=True)
    booking = relationship("Booking", back_populates="payment")
