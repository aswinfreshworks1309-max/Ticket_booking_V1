from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=schemas.PaymentResponse)
def create_payment(payload: schemas.PaymentCreate, db: Session = Depends(get_db)):
    try:
        pay = crud.create_payment(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return pay

@router.get("/", response_model=list[schemas.PaymentResponse])
def list_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_payments(db, skip=skip, limit=limit)

@router.get("/{payment_id}", response_model=schemas.PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = crud.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.put("/{payment_id}", response_model=schemas.PaymentResponse)
def update_payment(payment_id: int, status: str, db: Session = Depends(get_db)):
    payment = crud.update_payment_status(db, payment_id, status)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    success = crud.delete_payment(db, payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}
