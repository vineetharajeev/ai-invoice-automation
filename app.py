import os
import io
import re
import csv
import json

import pymupdf
import pytesseract

from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
from google import genai

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Depends
)
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session


# -----------------------------
# CONFIGURATION
# -----------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY else None
)

app = FastAPI(title="AI Invoice Automation")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# -----------------------------
# DATABASE CONFIGURATION
# -----------------------------

DATABASE_URL = "sqlite:///./invoices.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String)
    invoice_number = Column(String)
    date = Column(String)
    amount = Column(Float)
    tax = Column(Float)
    status = Column(String, default="Pending")


Base.metadata.create_all(bind=engine)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# -----------------------------
# HOME
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "AI Invoice Automation API is running!"
    }


# -----------------------------
# CREATE INVOICE
# -----------------------------

@app.post("/invoices")
def create_invoice(
    vendor: str,
    invoice_number: str,
    date: str,
    amount: float,
    tax: float,
    db: Session = Depends(get_db)
):

    invoice = Invoice(
        vendor=vendor,
        invoice_number=invoice_number,
        date=date,
        amount=amount,
        tax=tax
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return {
        "message": "Invoice saved successfully",
        "invoice_id": invoice.id
    }


# -----------------------------
# GET ALL INVOICES
# -----------------------------

@app.get("/invoices")
def get_invoices(db: Session = Depends(get_db)):

    return db.query(Invoice).all()


# -----------------------------
# INVOICE TEXT EXTRACTION
# -----------------------------

@app.post("/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    extracted_text = ""

    # PDF EXTRACTION
    if file.content_type == "application/pdf":

        try:

            pdf_document = pymupdf.open(
                stream=contents,
                filetype="pdf"
            )

            for page in pdf_document:

                page_text = page.get_text()

                if page_text.strip():

                    extracted_text += page_text + "\n"

                else:

                    pix = page.get_pixmap(dpi=200)

                    image = Image.open(
                        io.BytesIO(pix.tobytes("png"))
                    ).convert("RGB")

                    extracted_text += (
                        pytesseract.image_to_string(image) + "\n"
                    )

            pdf_document.close()

        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=f"PDF processing failed: {str(e)}"
            )

    # IMAGE EXTRACTION
    elif file.content_type in ["image/png", "image/jpeg"]:

        try:

            image = Image.open(
                io.BytesIO(contents)
            ).convert("RGB")

            extracted_text = pytesseract.image_to_string(image)

        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=f"Image processing failed: {str(e)}"
            )

    else:

        raise HTTPException(
            status_code=400,
            detail="Only PDF, PNG and JPG files are supported"
        )

    print("========== EXTRACTED TEXT ==========")
    print(extracted_text)
    print("====================================")

    invoice_data = extract_invoice_data(extracted_text)

    print("EXTRACTION RESULT:", invoice_data)

    return {
        "message": "Invoice processed successfully",
        "extracted_text": extracted_text,
        "invoice_data": invoice_data
    }


# -----------------------------
# AI + REGEX EXTRACTION
# -----------------------------

def extract_invoice_data(text):

    text = text.replace("\u00a0", " ")
    text = text.replace("US$", "$")

    # GEMINI AI EXTRACTION
    # One attempt only to avoid wasting quota.

    if gemini_client and text.strip():

        prompt = f"""
        Extract invoice information from the text below.

        Return ONLY JSON with these keys:
        vendor, invoice_number, date, due_date,
        subtotal, tax, total.

        Use null for missing values.
        Amounts must be numbers.
        Do not guess.

        Invoice text:
        {text}
        """

        try:

            response = gemini_client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            ai_data = json.loads(response.text)

            return {
                "vendor": ai_data.get("vendor") or "Not Found",
                "invoice_number": ai_data.get("invoice_number") or "Not Found",
                "date": ai_data.get("date") or "Not Found",
                "due_date": ai_data.get("due_date") or "Not Found",
                "subtotal": ai_data.get("subtotal"),
                "tax": ai_data.get("tax"),
                "total": ai_data.get("total"),
                "extraction_method": "Gemini AI"
            }

        except Exception as e:

            print("Gemini unavailable. Using Regex:", e)

    # REGEX FALLBACK

    print("Using Regex fallback...")

    # Invoice number
    invoice_number = re.search(
        r"Invoice\s*(?:Number|No\.?|#)?\s*[:#]?\s*([A-Z0-9-]+)",
        text,
        re.IGNORECASE
    )

    # Date patterns
    date_pattern = (
        r"([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}"
        r"|\d{4}-\d{2}-\d{2}"
        r"|\d{1,2}[/-]\d{1,2}[/-]\d{4})"
    )

    date = re.search(
        r"(?:Invoice\s+Date|Date\s+Issued|Issue\s+Date|Date)"
        r"\s*[:\-]?\s*" + date_pattern,
        text,
        re.IGNORECASE
    )

    due_date = re.search(
        r"(?:Due\s+Date|Payment\s+Due|Due)"
        r"\s*[:\-]?\s*" + date_pattern,
        text,
        re.IGNORECASE
    )

    # Amount patterns
    amount_pattern = (
        r"(?:USD\s*|\$\s*)?"
        r"([\d,]+(?:\.\d{1,2})?)"
        r"(?:\s*USD)?"
    )

    def get_amount(labels):

        pattern = (
            r"(?:" + labels + r")"
            r"\s*[:\-]?\s*" + amount_pattern
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return float(
                match.group(1).replace(",", "")
            )

        return None

    subtotal = get_amount(
        r"Sub[\s-]?total"
    )

    tax = get_amount(
        r"Tax|Sales\s+Tax|VAT"
    )

    total = get_amount(
        r"Grand\s+Total|Total\s+Due|Amount\s+Due|Balance\s+Due|Total"
    )

    # Vendor detection
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    vendor = "Not Found"

    for line in lines:

        if not re.search(
            r"invoice|date|due|subtotal|sub-total|tax|total|"
            r"amount|balance|bill\s+to|ship\s+to|"
            r"phone|email|www\.|http",
            line,
            re.IGNORECASE
        ):

            vendor = line
            break

    return {

        "vendor": vendor,

        "invoice_number": (
            invoice_number.group(1)
            if invoice_number else "Not Found"
        ),

        "date": (
            date.group(1)
            if date else "Not Found"
        ),

        "due_date": (
            due_date.group(1)
            if due_date else "Not Found"
        ),

        "subtotal": subtotal,
        "tax": tax,
        "total": total,

        "extraction_method": "Regex Fallback"
    }


# -----------------------------
# APPROVE INVOICE
# -----------------------------

@app.post("/approve-invoice")
def approve_invoice(
    vendor: str,
    invoice_number: str,
    date: str,
    amount: float,
    tax: float,
    db: Session = Depends(get_db)
):

    invoice = Invoice(
        vendor=vendor,
        invoice_number=invoice_number,
        date=date,
        amount=amount,
        tax=tax,
        status="Approved"
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return {
        "message": "Invoice approved and saved successfully",
        "invoice_id": invoice.id,
        "status": invoice.status
    }


# -----------------------------
# APPROVE EXTRACTED INVOICE
# -----------------------------

@app.post("/approve-extracted-invoice")
def approve_extracted_invoice(
    vendor: str,
    invoice_number: str,
    date: str,
    due_date: str,
    subtotal: float,
    tax: float,
    total: float,
    db: Session = Depends(get_db)
):

    invoice = Invoice(
        vendor=vendor,
        invoice_number=invoice_number,
        date=date,
        amount=total,
        tax=tax,
        status="Approved"
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return {
        "message": "Extracted invoice approved successfully",
        "invoice_id": invoice.id,
        "invoice_data": {
            "vendor": invoice.vendor,
            "invoice_number": invoice.invoice_number,
            "date": invoice.date,
            "total": invoice.amount,
            "tax": invoice.tax,
            "status": invoice.status
        }
    }


# -----------------------------
# DASHBOARD
# -----------------------------

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):

    invoices = db.query(Invoice).all()

    total_invoices = len(invoices)

    total_expenses = sum(
        invoice.amount or 0
        for invoice in invoices
    )

    approved = sum(
        1 for invoice in invoices
        if invoice.status == "Approved"
    )

    pending = sum(
        1 for invoice in invoices
        if invoice.status == "Pending"
    )

    return {
        "total_invoices": total_invoices,
        "total_expenses": total_expenses,
        "approved_invoices": approved,
        "pending_invoices": pending
    }


# -----------------------------
# SEARCH INVOICES
# -----------------------------

@app.get("/search-invoices")
def search_invoices(
    keyword: str,
    db: Session = Depends(get_db)
):

    invoices = db.query(Invoice).filter(
        (Invoice.vendor.ilike(f"%{keyword}%")) |
        (Invoice.invoice_number.ilike(f"%{keyword}%"))
    ).all()

    return invoices


# -----------------------------
# FILTER INVOICES
# -----------------------------

@app.get("/filter-invoices")
def filter_invoices(
    status: str,
    db: Session = Depends(get_db)
):

    invoices = db.query(Invoice).filter(
        Invoice.status == status
    ).all()

    return invoices


# -----------------------------
# EXPORT CSV
# -----------------------------

@app.get("/export-invoices")
def export_invoices(db: Session = Depends(get_db)):

    invoices = db.query(Invoice).all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Vendor",
        "Invoice Number",
        "Date",
        "Amount",
        "Tax",
        "Status"
    ])

    for invoice in invoices:

        writer.writerow([
            invoice.id,
            invoice.vendor,
            invoice.invoice_number,
            invoice.date,
            invoice.amount,
            invoice.tax,
            invoice.status
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=invoices.csv"
        }
    )


# -----------------------------
# MONTHLY EXPENSE ANALYTICS
# -----------------------------

@app.get("/monthly-expenses")
def monthly_expenses(db: Session = Depends(get_db)):

    invoices = db.query(Invoice).filter(
        Invoice.status == "Approved"
    ).all()

    monthly_totals = {}

    for invoice in invoices:

        try:

            date_obj = None

            for date_format in (
                "%Y-%m-%d",
                "%b %d, %Y",
                "%B %d, %Y",
                "%m/%d/%Y",
                "%d/%m/%Y"
            ):

                try:

                    date_obj = datetime.strptime(
                        invoice.date,
                        date_format
                    )

                    break

                except ValueError:
                    continue

            if date_obj is None:
                continue

            month = date_obj.strftime("%Y-%m")

            if month not in monthly_totals:
                monthly_totals[month] = 0

            monthly_totals[month] += invoice.amount or 0

        except (ValueError, TypeError):
            continue

    return [
        {
            "month": month,
            "total_expenses": total
        }
        for month, total in sorted(monthly_totals.items())
    ]
