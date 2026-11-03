# AI Invoice Automation System

An AI-powered invoice processing and expense management application built using **Python, FastAPI, OCR, and Google Gemini API**. The system automates invoice data extraction, reduces manual data entry, and organizes extracted information for efficient expense tracking.

## Overview

Processing invoices manually can be time-consuming and error-prone. This project addresses that problem by combining Optical Character Recognition (OCR) with Generative AI to extract structured information from uploaded invoice documents.

The application uses Tesseract OCR to extract text from documents and Google Gemini API to interpret invoice content and identify relevant information. It also includes a regex-based fallback mechanism to support extraction when AI processing is unavailable.

## Key Features

- **Multi-format Invoice Upload:** Upload invoices in PDF, PNG, and JPG formats.
- **OCR Processing:** Extract text from invoice documents using Tesseract OCR.
- **AI-Powered Data Extraction:** Use Google Gemini API to identify and extract relevant invoice information.
- **Fallback Extraction:** Use regex-based extraction when Gemini API processing is unavailable.
- **Invoice Management:** Review and approve extracted invoice records.
- **Database Integration:** Store invoice information using SQLite and SQLAlchemy.
- **Search and Filtering:** Find and filter stored invoice records.
- **Expense Analytics Dashboard:** View expense summaries and analytics.
- **Monthly Expense Visualization:** Analyze monthly expenses using interactive charts.
- **CSV Export:** Export invoice records for reporting and further analysis.

## System Architecture

The application follows a modular document-processing workflow:

```text
       User
         |
         v
   Upload Invoice
    (PDF / PNG / JPG)
         |
         v
    FastAPI Backend
         |
         v
    Document Processing
         |
         v
      Tesseract OCR
         |
         v
    Extracted Text
         |
         v
     Google Gemini API
         |
         v
   Structured Invoice Data
         |
         v
    Regex Fallback
   (When AI unavailable)
         |
         v
    Invoice Review
         |
         v
    User Approval
         |
         v
   SQLite Database
         |
         v
 Expense Dashboard & CSV Export
```

## Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| AI Integration | Google Gemini API |
| OCR | Tesseract OCR |
| PDF Processing | PyMuPDF |
| Image Processing | Pillow |
| Database | SQLite |
| ORM | SQLAlchemy |
| Frontend | HTML, CSS, JavaScript |
| Data Visualization | Chart.js |
| Environment Management | Python Virtual Environment, python-dotenv |
| Version Control | Git, GitHub |

## How AI Is Used

Google Gemini API is integrated to interpret invoice text extracted through OCR and convert relevant information into structured invoice data.

The AI integration helps with:

- Understanding unstructured invoice text.
- Identifying relevant invoice information.
- Extracting information into structured fields.
- Reducing repetitive manual data entry.

A regex-based fallback mechanism is included to provide an alternative extraction approach when Gemini API processing is unavailable.

**Engineering consideration:** AI-generated information should be reviewed before approval and storage. AI extraction is not guaranteed to be error-free.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/vineetharajeev/ai-invoice-automation.git

cd ai-invoice-automation
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install fastapi "uvicorn[standard]" sqlalchemy python-multipart pillow pytesseract pymupdf python-dotenv google-genai
```

### 5. Install Tesseract OCR

Install Tesseract OCR on your system and configure its executable path in the application.

Make sure Tesseract is accessible to the Python application.

### 6. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your own Gemini API key.

**Security:** Never commit your `.env` file or expose API credentials in a public repository.

### 7. Run the Application

```bash
uvicorn app:app --reload
```

### 8. Open the Application

Visit:

```text
http://127.0.0.1:8000
```

## Project Structure

```text
ai-invoice-automation/
│
├── app.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
│
├── templates/
│
├── static/
│
└── ...
```

*Note: Update this structure to match the actual files and folders in your repository.*

## Learning Outcomes

Through this project, I explored:

- Integrating third-party AI APIs into Python applications.
- Building backend applications using FastAPI.
- Processing PDF and image-based documents.
- Combining OCR with Generative AI for document understanding.
- Implementing fallback mechanisms for AI service failures.
- Managing application data using SQLAlchemy and SQLite.
- Using Git and GitHub for project development and version control.
- Using AI-assisted development tools to explore solutions, debug issues, and improve development workflows.

## Future Improvements

- Add support for more invoice formats and layouts.
- Improve extraction accuracy through structured output validation.
- Introduce automated invoice data verification.
- Add authentication and role-based access control.
- Support additional database systems.
- Deploy the application for public access.

## Author

**Vineetha P R**

GitHub: [@vineetharajeev](https://github.com/vineetharajeev)
