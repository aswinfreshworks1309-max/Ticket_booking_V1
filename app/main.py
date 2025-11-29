from fastapi import FastAPI
from .database import engine, Base
from .routers import buses, schedules, seats, bookings, payments, users

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables (for development)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="LOCOTRANZ — Bus Booking API", lifespan=lifespan)

app.include_router(users.router)
app.include_router(buses.router)
app.include_router(schedules.router)
app.include_router(seats.router)
app.include_router(bookings.router)
app.include_router(payments.router)

@app.get("/")
def root():
    return {"msg": "LOCOTRANZ API running"}
