"""
File: main.py
Purpose:
    - This FastAPI application serves as the main entry point for the OCR app.
    - It provides a web interface for uploading PDF files.
    - It uses pdfplumber to extract raw text from the uploaded PDF.
    - It then calls our custom parsing module (parse_bol_spacy.py) to structure the extracted text
      into a JSON object matching the desired output.
    - The structured JSON is returned as the API response.
    
Role & Relation:
    - main.py defines two endpoints:
        • GET "/" returns an HTML upload form.
        • POST "/upload" accepts a PDF file, extracts text, parses it, and returns structured JSON.
Workflow Integration:
    1. The user accesses the home page and uploads a PDF file.
    2. The /upload endpoint extracts text using pdfplumber.
    3. The raw text is passed to the parse_bol_spacy() function.
    4. The structured JSON data is returned as the API response.
Educational Comments:
    - pdfplumber is used for robust PDF text extraction.
    - Our parsing logic in parse_bol_spacy.py combines regex and spaCy for improved accuracy without hard-coding specific names.
"""

import io
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pdfplumber

# Import our custom parsing module
from parse_bol_spacy import parse_bol_spacy

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    GET endpoint to serve the HTML upload form.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=JSONResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    POST endpoint to process the uploaded PDF.
    Steps:
      1. Validate the file type.
      2. Read the PDF file and extract text using pdfplumber.
      3. Pass the extracted text to the parse_bol_spacy() function to obtain structured JSON.
      4. Return the structured JSON as the response.
    """
    if file.content_type != "application/pdf":
        return JSONResponse(content={"error": "Invalid file type. Please upload a PDF."}, status_code=400)
    try:
        contents = await file.read()
        # Open the PDF and extract text from all pages.
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            raw_text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )
        # Parse the raw text to produce structured JSON.
        parsed_data = parse_bol_spacy(raw_text)
        return {"parsed_data": parsed_data}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
