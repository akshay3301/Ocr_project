from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import os
from database import init_db
from services.file_service import validate_pdf
from services.ocr_service import process_receipt
from database import SessionLocal
from models.models import ReceiptFile, Receipt


app = FastAPI()
UPLOAD_DIR = Path("receipts")
UPLOAD_DIR.mkdir(exist_ok=True)

init_db()

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db = SessionLocal()
    receipt_file = ReceiptFile(
        file_name=file.filename,
        file_path=str(file_path),
    )
    db.add(receipt_file)
    db.commit()
    db.refresh(receipt_file)
    db.close()

    return {"message": "File uploaded successfully", "id": receipt_file.id}

@app.post("/validate")
def validate(receipt_id: int):
    db = SessionLocal()
    receipt_file = db.query(ReceiptFile).filter_by(id=receipt_id).first()
    if not receipt_file:
        db.close()
        raise HTTPException(status_code=404, detail="Receipt not found")

    is_valid, reason = validate_pdf(receipt_file.file_path)
    receipt_file.is_valid = is_valid
    receipt_file.invalid_reason = reason if not is_valid else None
    db.commit()
    db.close()
    return {"is_valid": is_valid, "invalid_reason": reason}

@app.post("/process")
def process(receipt_id: int):
    db = SessionLocal()
    receipt_file = db.query(ReceiptFile).filter_by(id=receipt_id, is_valid=True).first()
    if not receipt_file:
        db.close()
        raise HTTPException(status_code=404, detail="Receipt not found or not valid")

    # # Check if file already processed (exists in Receipt table)
    # existing_receipt = db.query(Receipt).filter_by(file_path=receipt_file.file_path).first()
    # if existing_receipt:
    #     db.close()
    #     raise HTTPException(status_code=400, detail="File already exists")

    data = process_receipt(receipt_file.file_path)
    receipt = Receipt(
        purchased_at=data["purchased_at"],
        merchant_name=data["merchant_name"],
        total_amount=data["total_amount"],
        file_path=receipt_file.file_path
    )
    db.add(receipt)
    receipt_file.is_processed = True
    db.commit()
    db.close()
    return {"message": "Receipt processed successfully"}

@app.get("/receipts")
def get_all_receipts():
    db = SessionLocal()
    receipts = db.query(Receipt).all()
    db.close()
    return receipts

@app.get("/receipts/{receipt_id}")
def get_receipt(receipt_id: int):
    db = SessionLocal()
    receipt = db.query(Receipt).filter_by(id=receipt_id).first()
    db.close()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt