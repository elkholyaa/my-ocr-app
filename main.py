"""
File: main.py
Purpose:
    - This FastAPI application serves as the main entry point for the OCR app.
    - It provides a web interface for uploading PDF files, extracts text using pdfplumber,
      and processes the text with spaCy to extract entities.
    - The processed data is returned as structured JSON.
Role & Relation:
    - main.py defines two endpoints:
        • GET "/" returns an HTML form for file upload.
        • POST "/upload" processes the uploaded PDF.
Workflow Integration:
    1. The user accesses the home page and uploads a PDF file.
    2. The "/upload" endpoint reads the file, extracts text via pdfplumber, and processes it with spaCy.
    3. The response includes both the raw extracted text and the recognized entities.
Educational Comments:
    - pdfplumber handles complex PDF layouts better than simple regex extraction.
    - spaCy is used to perform NLP on the extracted text. The pre-trained model "en_core_web_sm" is used here.
    - This is a basic implementation that you can extend for custom entity extraction or more advanced processing.
"""

import io
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pdfplumber
import spacy

# Create the FastAPI app and set up the Jinja2 templates directory.
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load the spaCy model (ensure you have run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

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
      3. Process the extracted text with spaCy to obtain named entities.
      4. Return a JSON response containing the raw text and entities.
    """
    if file.content_type != "application/pdf":
        return JSONResponse(content={"error": "Invalid file type. Please upload a PDF."}, status_code=400)

    try:
        contents = await file.read()
        # Extract text from the PDF using pdfplumber.
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            full_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        
        # Process the extracted text with spaCy.
        doc = nlp(full_text)
        entities = [{"label": ent.label_, "text": ent.text} for ent in doc.ents]

        # Return both raw text and recognized entities.
        return {"raw_text": full_text, "entities": entities}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
