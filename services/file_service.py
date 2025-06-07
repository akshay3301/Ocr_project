from PyPDF2 import PdfReader

def validate_pdf(file_path: str):
    try:
        PdfReader(file_path)
        return True, None
    except Exception as e:
        return False, str(e)