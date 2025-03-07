# My OCR App (Python Edition)

## Overview

This is a Proof-of-Concept (POC) OCR application built with FastAPI. It allows users to upload PDF files (e.g., Bills of Lading) and extracts text using pdfplumber. The extracted text is further processed using spaCy for named entity recognition, and the results are returned as JSON.

## Features

- Upload PDF files via a web interface.
- Extract text robustly using pdfplumber.
- Process text with spaCy to recognize entities.
- Return structured JSON data containing raw text and recognized entities.

## Technology Stack

- **FastAPI**: Web framework for building APIs.
- **uvicorn**: ASGI server.
- **pdfplumber**: PDF text extraction.
- **spaCy**: Natural language processing.
- **Jinja2**: Templating engine for HTML pages.
- **Bootstrap**: For basic frontend styling (via CDN).

## Setup Instructions

1. Clone or download the project files.
2. Navigate to the project folder:
   ```bash
   cd my-ocr-app-python
