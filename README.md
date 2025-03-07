# My OCR App (Python Edition)

## Overview

This is a Proof-of-Concept (POC) OCR application built with FastAPI. It allows users to upload PDF files (e.g., Bills of Lading) and extracts text using pdfplumber. The extracted text is then parsed using a combination of regex and spaCy (in `parse_bol_spacy.py`) to produce a structured JSON output.

## Features

- Upload PDF files via a web interface.
- Extract text from PDFs using pdfplumber.
- Parse the extracted text to generate structured JSON data.
- Returns key shipment details such as:
  - BILL_OF_LADING_No
  - SHIPPER
  - CONSIGNEE
  - Total_Gross_Weight
  - Total_Items
  - Number_of_Containers
  - Detailed container information

## Technology Stack

- **FastAPI**: Web framework for building APIs.
- **uvicorn**: ASGI server.
- **pdfplumber**: PDF text extraction.
- **spaCy**: Natural language processing (used for entity extraction).
- **Jinja2**: Templating engine for HTML.
- **python-multipart**: For handling form data.

## Setup Instructions

1. Clone or download the project files.
2. Navigate to the project folder:
   ```bash
   cd my-ocr-app-python
