
# AI Invoice & Expense Automation System

An AI-powered invoice processing application built using Python, FastAPI, OCR and Google Gemini API.

## Features

- Upload invoices in PDF, PNG and JPG formats
- Extract invoice details automatically
- OCR-based text extraction using Tesseract
- AI-powered invoice data extraction using Gemini
- Regex fallback when AI extraction is unavailable
- Review and approve invoices
- Store invoice records using SQLite
- Search and filter invoices
- Dashboard with expense analytics
- Monthly expense visualization
- Export invoice records as CSV

## Technologies Used

- Python
- FastAPI
- Google Gemini API
- Tesseract OCR
- PyMuPDF
- SQLAlchemy
- SQLite
- HTML, CSS and JavaScript
- Chart.js

## Run Locally

1. Clone this repository.
2. Create a virtual environment:

   `python -m venv .venv`

3. Activate it:

   `.venv\Scripts\activate`

4. Install dependencies:

   `pip install fastapi "uvicorn[standard]" sqlalchemy python-multipart pillow pytesseract pymupdf python-dotenv google-genai`

5. Install Tesseract OCR and configure its path in the application.
6. Create a `.env` file and add your Gemini API key:

   `GEMINI_API_KEY=your_api_key_here`

7. Start the application:

   `uvicorn app:app --reload`

8. Open `http://127.0.0.1:8000` in your browser.

## Note

Gemini API access requires a valid API key and available quota. Regex-based extraction is used as a fallback when Gemini is unavailable.
