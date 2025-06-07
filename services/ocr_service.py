import pytesseract
from pdf2image import convert_from_path
import re
from datetime import datetime
import platform
import os

def process_receipt(file_path: str):
    # Detect OS and set poppler_path accordingly
    poppler_path = None
    if platform.system() == "Windows":
        poppler_path = r"C:\poppler-24.08.0\Library\bin"  # Change this if your path is different
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
    images = convert_from_path(file_path, poppler_path=poppler_path)
    text = pytesseract.image_to_string(images[0])  # assume single page receipt
    print(text)
    date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", text)
    time_match = re.search(r"\b(\d{1,2}:\d{2}(?:\s?[AP]M)?)\b", text)
    amount_match = re.search(r"Total\s*[:\-]?\s*[$₹]?(\d+\.?\d*)", text, re.IGNORECASE)
    merchant_match = re.search(r"^(.*?)(?:\n|$)", text) 

    file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_merchant_name = re.sub(r'[_\d]+$', '', file_name)

    purchased_at = None
    try:
        if date_match:
            purchased_at = date_match.group(1) + " " + time_match.group(0) if time_match else date_match.group(1)
            purchased_at = datetime.strptime(purchased_at, "%d/%m/%Y %I:%M %p") if "/" in purchased_at else datetime.strptime(purchased_at, "%d-%m-%Y %I:%M %p")
    except:
        purchased_at = None

    # Compare merchant_match with file_merchant_name (case-insensitive, stripped)
    ocr_merchant = merchant_match.group(1).strip() if merchant_match else ""
    if ocr_merchant.lower() == file_merchant_name.lower():
        merchant_name = ocr_merchant
    else:
        merchant_name = file_merchant_name

    return {
        "purchased_at": purchased_at,
        "merchant_name": merchant_name,
        "total_amount": float(amount_match.group(1)) if amount_match else 0.0
    }
