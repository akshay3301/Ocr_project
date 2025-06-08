import requests
import os
import re
from datetime import datetime
import platform
import pytesseract
from pdf2image import convert_from_path
from dotenv import load_dotenv
from os import getenv
load_dotenv()
ocr_api_key = getenv("API_KEY")

def ocr_space_api(file_path, api_key=ocr_api_key):
    """
    OCR.Space API for receipt text extraction (supports PDF directly)
    """
    url = 'https://api.ocr.space/parse/image'
    
    with open(file_path, 'rb') as f:
        response = requests.post(
            url,
            files={'file': f},
            data={
                'apikey': api_key,
                'language': 'eng',
                'isOverlayRequired': False,
                'OCREngine': 2,
                'detectOrientation': True,
                'scale': True,
                'filetype': 'PDF' if file_path.lower().endswith('.pdf') else 'Auto'
            }
        )
    
    if response.status_code == 200:
        result = response.json()
        if not result['IsErroredOnProcessing']:
            return result['ParsedResults'][0]['ParsedText']
    return None

def tesseract_fallback(file_path):
    """
    Tesseract fallback OCR
    """
    try:
        poppler_path = None
        if platform.system() == "Windows":
            poppler_path = r"C:\poppler-24.08.0\Library\bin"
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        images = convert_from_path(file_path, poppler_path=poppler_path)
        text = pytesseract.image_to_string(images[0])
        return text
    except Exception as e:
        print(f"Tesseract failed: {e}")
        return None

def process_receipt(file_path: str):
    
    
    
    try:
        text = ocr_space_api(file_path, ocr_api_key)
        if text:
            print("Used OCR.Space (direct PDF)")
    except Exception as e:
        print(f"OCR.Space direct PDF failed: {e}")
    
    
    if not text:
        try:
            poppler_path = None
            if platform.system() == "Windows":
                poppler_path = r"C:\poppler-24.08.0\Library\bin"
            
            images = convert_from_path(file_path, poppler_path=poppler_path)
            temp_image_path = "temp_receipt.jpg"
            images[0].save(temp_image_path, 'JPEG')
            
            text = ocr_space_api(temp_image_path, ocr_api_key)
            os.remove(temp_image_path)
            
            if text:
                print("Used OCR.Space (via image conversion)")
        except Exception as e:
            print(f"OCR.Space image conversion failed: {e}")
    
    # Fallback to Tesseract
    if not text:
        text = tesseract_fallback(file_path)
        if text:
            print("Used Tesseract")
    
    if not text:
        text = ""
        print("All OCR methods failed")
    
    print(text)
    
    
    date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", text)
    time_match = re.search(r"\b(\d{1,2}:\d{2})\b", text)
    
    filename_date_match = None
    if not date_match:
        filename = os.path.basename(file_path)
        filename_date_match = re.search(r"(\d{4})(\d{2})(\d{2})", filename)
    
   
    amount_match = None
    
    
    decimal_amounts = re.findall(r'\b(\d+\.\d{2})\b', text)
    if decimal_amounts:
        float_amounts = [float(amt) for amt in decimal_amounts]
        largest_amount = max(float_amounts)
        amount_match = type('Match', (), {'group': lambda self, n: str(largest_amount)})()
        print(f"Found decimal amounts: {decimal_amounts}, largest: {largest_amount}")
    else:
      
        general_amounts = re.findall(r'\b(\d+\.?\d*)\b', text)
        if general_amounts:
            monetary_amounts = []
            for amt in general_amounts:
                try:
                    float_val = float(amt)
                    if 0.01 <= float_val <= 10000:
                        monetary_amounts.append(float_val)
                except ValueError:
                    continue
            
            if monetary_amounts:
                largest_amount = max(monetary_amounts)
                amount_match = type('Match', (), {'group': lambda self, n: str(largest_amount)})()
                print(f"Found general amounts: {monetary_amounts}, largest: {largest_amount}")
    
    
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]
    
    
    if '_' in filename_without_ext:
        filename_merchant = filename_without_ext.split('_')[0].strip()
    else:
        filename_merchant = filename_without_ext.strip()
    
   
    merchant_name = "Unknown"
    if filename_merchant and text:
        
        escaped_merchant = re.escape(filename_merchant)
        pattern = r'\b' + escaped_merchant + r'\b'
        
        if re.search(pattern, text, re.IGNORECASE):
            
            merchant_name = ' '.join(word.capitalize() for word in filename_merchant.split())
            print(f"Found filename merchant '{filename_merchant}' in OCR text")
        else:
            
            merchant_name = ' '.join(word.capitalize() for word in filename_merchant.split())
            print(f"Filename merchant '{filename_merchant}' not found in OCR text, using filename anyway")
    else:
        
        if filename_merchant:
            merchant_name = ' '.join(word.capitalize() for word in filename_merchant.split())
        else:
            merchant_name = "Unknown"
    
 
    purchased_at = None
    if date_match:
        date_str = date_match.group(1)
        date_formats = ["%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y", 
                       "%d/%m/%y", "%m/%d/%y", "%d-%m-%y", "%m-%d-%y"]
        
        for fmt in date_formats:
            try:
                purchased_at = datetime.strptime(date_str, fmt)
               
                if time_match:
                    time_str = time_match.group(1)
                    try:
                        time_obj = datetime.strptime(time_str, "%H:%M").time()
                        purchased_at = purchased_at.replace(hour=time_obj.hour, minute=time_obj.minute)
                    except ValueError:
                        pass
                break
            except ValueError:
                continue
    elif filename_date_match:
        try:
            year, month, day = filename_date_match.groups()
            purchased_at = datetime(int(year), int(month), int(day))
            
            if time_match:
                time_str = time_match.group(1)
                try:
                    time_obj = datetime.strptime(time_str, "%H:%M").time()
                    purchased_at = purchased_at.replace(hour=time_obj.hour, minute=time_obj.minute)
                except ValueError:
                    pass
        except ValueError:
            purchased_at = None
    

    total_amount = 0.0
    if amount_match:
        try:
            amount_str = amount_match.group(1)
           
            if '.' not in amount_str and len(amount_str) > 2:
                if len(amount_str) >= 3:
                    amount_str = amount_str[:-2] + '.' + amount_str[-2:]
            total_amount = float(amount_str)
        except (ValueError, IndexError, AttributeError):
            total_amount = 0.0
    
    return {
        "purchased_at": purchased_at, 
        "merchant_name": merchant_name,
        "total_amount": total_amount
    }