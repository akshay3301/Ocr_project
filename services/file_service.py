from PyPDF2 import PdfReader
import hashlib

def validate_pdf(file_path: str):
    try:
        PdfReader(file_path)
        return True, None
    except Exception as e:
        return False, str(e)

def get_file_hash(file) -> str:
    hasher = hashlib.sha256()
    file.seek(0)  
    while chunk := file.read(8192):
        hasher.update(chunk)
    file.seek(0)
    return hasher.hexdigest()
