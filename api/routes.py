from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import tempfile
from datetime import datetime

from models.mcq_models import MCQRequest, DocumentMCQRequest, MCQSource
from core.mcq_generator import MCQGenerator
from core.document_processor import DocumentProcessor
from core.vector_store import VectorStore
from core.external_apis import ExternalAPIs
from core.email_sender import EmailSender
from core.google_drive import GoogleDriveUploader
from utils.pdf_generator import PDFGenerator
from utils.logger import logger

app = FastAPI(title="MCQ AI Agent", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Initialize components
mcq_generator = MCQGenerator()
document_processor = DocumentProcessor()
vector_store = VectorStore()
external_apis = ExternalAPIs()
email_sender = EmailSender()
drive_uploader = GoogleDriveUploader()

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

@app.post("/generate-domain-mcq")
async def generate_domain_mcq(request: MCQRequest):
    """Generate MCQs for a specific domain"""
    try:
        # Get content based on source
        if request.source == MCQSource.SERP_API:
            content = external_apis.search_serp_api(request.domain)
        elif request.source == MCQSource.WIKIPEDIA:
            content = external_apis.search_wikipedia(request.domain)
        else:
            content = None
        
        # Generate MCQs
        if content:
            mcqs = mcq_generator.generate_mcqs_from_context(
                content, request.count, request.difficulty, request.custom_prompt
            )
        else:
            mcqs = mcq_generator.generate_mcqs_from_domain(
                request.domain, request.count, request.difficulty
            )
        
        # Generate PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"mcq_{request.domain}_{timestamp}.pdf"
        pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)
        
        PDFGenerator.generate_mcq_pdf(mcqs, pdf_path, f"MCQ Assessment - {request.domain}")
        
        # Upload to Google Drive
        drive_file_id = drive_uploader.upload_file(pdf_path, pdf_filename)
        
        # Send email if requested
        if request.email:
            email_sender.send_mcq_pdf(request.email, pdf_path)
        
        return {
            "success": True,
            "mcq_count": len(mcqs),
            "pdf_path": pdf_path,
            "drive_file_id": drive_file_id,
            "message": "MCQs generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating domain MCQs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-document-mcq")
async def upload_document_mcq(
    file: UploadFile = File(...),
    count: int = Form(10),
    difficulty: str = Form("medium"),
    email: Optional[str] = Form(None),
    custom_prompt: Optional[str] = Form(None)
):
    """Generate MCQs from uploaded document"""
    try:
        logger.info(f"Processing document upload with email: {email}")
        
        # Validate email if provided
        if email and email.strip() == "":
            email = None
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        logger.info(f"Temporary file created: {tmp_file_path}")
        
        # Extract text
        text = document_processor.extract_text_from_file(tmp_file_path)
        
        if not text or text.strip() == "":
            raise ValueError("No text could be extracted from the uploaded document")
        
        logger.info(f"Extracted text length: {len(text)} characters")
        
        # Add to vector store
        vector_store.add_document(text, {"filename": file.filename})
        
        # Generate MCQs
        mcqs = mcq_generator.generate_mcqs_from_context(text, count, difficulty, custom_prompt)
        
        if not mcqs:
            raise ValueError("No MCQs could be generated from the document")
        
        logger.info(f"Generated {len(mcqs)} MCQs")
        
        # Generate PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        pdf_filename = f"mcq_{safe_filename}_{timestamp}.pdf"
        pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)
        
        PDFGenerator.generate_mcq_pdf(mcqs, pdf_path, f"MCQ Assessment - {file.filename}")
        
        logger.info(f"PDF generated: {pdf_path}")
        
        # Upload to Google Drive
        try:
            drive_file_id = drive_uploader.upload_file(pdf_path, pdf_filename)
            logger.info(f"File uploaded to Google Drive: {drive_file_id}")
        except Exception as drive_error:
            logger.error(f"Google Drive upload failed: {drive_error}")
            drive_file_id = None
        
        # Send email if requested
        email_sent = False
        if email and email.strip():
            try:
                logger.info(f"Attempting to send email to: {email}")
                email_sender.send_mcq_pdf(email.strip(), pdf_path)
                email_sent = True
                logger.info("Email sent successfully")
            except Exception as email_error:
                logger.error(f"Email sending failed: {email_error}")
                # Don't raise exception, just log the error
        
        # Cleanup temporary file
        try:
            os.unlink(tmp_file_path)
            logger.info("Temporary file cleaned up")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temporary file: {cleanup_error}")
        
        return {
            "success": True,
            "mcq_count": len(mcqs),
            "pdf_path": pdf_path,
            "drive_file_id": drive_file_id,
            "email_sent": email_sent,
            "message": "MCQs generated from document successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        # Cleanup temporary file in case of error
        try:
            if 'tmp_file_path' in locals():
                os.unlink(tmp_file_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    """Download generated PDF"""
    pdf_path = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")