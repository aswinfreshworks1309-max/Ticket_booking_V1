from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/buses", tags=["buses"])

@router.post("/", response_model=schemas.BusResponse)
def create_bus(bus: schemas.BusCreate, db: Session = Depends(get_db)):
    return crud.create_bus(db, bus)

@router.get("/", response_model=list[schemas.BusResponse])
def list_buses(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_buses(db, skip=skip, limit=limit)

@router.get("/{bus_id}", response_model=schemas.BusResponse)
def get_bus(bus_id: int, db: Session = Depends(get_db)):
    bus = crud.get_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus

@router.put("/{bus_id}", response_model=schemas.BusResponse)
def update_bus(bus_id: int, bus: schemas.BusCreate, db: Session = Depends(get_db)):
    updated_bus = crud.update_bus(db, bus_id, bus)
    if not updated_bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return updated_bus

@router.delete("/{bus_id}")
def delete_bus(bus_id: int, db: Session = Depends(get_db)):
    success = crud.delete_bus(db, bus_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bus not found")
    return {"message": "Bus deleted successfully"}
