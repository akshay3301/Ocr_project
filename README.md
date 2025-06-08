# 🧾 Receipt OCR App

A FastAPI-based web application to automate the extraction of data from scanned PDF receipts using OCR (Tesseract) and store structured metadata in an SQLite database.

---

## 📌 Features

- Upload scanned receipts in PDF format
- Validate if uploaded files are genuine PDFs
- Extract key information (merchant name, purchase date, total amount) using OCR
- Store extracted data in an SQLite database
- RESTful API for managing and querying receipt data

---

## 🗄️ Database Schema

### 1. `receipt_file` table

| Column Name   | Type      | Description                                      |
|---------------|-----------|--------------------------------------------------|
| `id`          | Integer   | Primary Key (autoincrement)                      |
| `file_name`   | String    | Name of the uploaded file                        |
| `file_path`   | String    | File system path where the file is stored        |
| `is_valid`    | Boolean   | Whether the file is a valid PDF                  |
| `invalid_reason` | String | Reason for invalidity if not a PDF              |
| `is_processed`| Boolean   | If OCR processing has been completed             |
| `created_at`  | DateTime  | Upload timestamp                                 |
| `updated_at`  | DateTime  | Last update timestamp                            |

### 2. `receipt` table

| Column Name     | Type      | Description                                   |
|------------------|-----------|-----------------------------------------------|
| `id`            | Integer   | Primary Key (autoincrement)                   |
| `purchased_at`  | DateTime  | Date of purchase extracted from the receipt   |
| `merchant_name` | String    | Extracted merchant/shop name                  |
| `total_amount`  | Float     | Extracted total amount from receipt           |
| `file_path`     | String    | File path linked to the receipt PDF           |
| `created_at`    | DateTime  | Record creation time                          |
| `updated_at`    | DateTime  | Record update time                            |

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR and Poppler

#### 📥 Tesseract (Windows):

- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add `C:\Program Files\Tesseract-OCR` to your system PATH
- Or add in code:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

#### 📥 Poppler (Windows):

- Download: https://github.com/oschwartz10612/poppler-windows/releases/
- Extract and add `C:\poppler\Library\bin` to your system PATH
- Or add in code:
```python
convert_from_path(file_path, poppler_path=r"C:\poppler\Library\bin")
```

---

## 🚀 Running the App

```bash
uvicorn main:app --reload
```

Visit the interactive API docs at:  
📄 http://127.0.0.1:8000/docs

---

## 📤 API Endpoints

### 1. **Upload a Receipt**
```http
POST /upload
```
**Body (form-data):**
- `file`: PDF file

**Response:**
```json
{
  "message": "File uploaded successfully",
  "id": 1
}
```

### 2. **Validate a Receipt File**
```http
POST /validate?receipt_id=1
```

**Response:**
```json
{
  "is_valid": true,
  "invalid_reason": null
}
```

### 3. **Process a Valid Receipt**
```http
POST /process?receipt_id=1
```

**Response:**
```json
{
  "message": "Receipt processed successfully"
}
```

### 4. **Get All Processed Receipts**
```http
GET /receipts
```

**Response:**
```json
[
  {
    "id": 1,
    "purchased_at": "2024-05-12T00:00:00",
    "merchant_name": "SuperMart",
    "total_amount": 244.50,
    "file_path": "receipts/receipt1.pdf"
  }
]
```

### 5. **Get Receipt by ID**
```http
GET /receipts/{receipt_id}
```

**Response:**
```json
{
  "id": 1,
  "purchased_at": "2024-05-12T00:00:00",
  "merchant_name": "SuperMart",
  "total_amount": 244.50
}
```

---

## 🧠 Tech Stack

- **Python** & **FastAPI**
- **SQLite** via SQLAlchemy ORM
- **Tesseract OCR** for text extraction
- **pdf2image + Poppler** for converting PDF to image
- **PyPDF2** for PDF validation

---

## 📎 License

MIT License – free to use, modify, and distribute.