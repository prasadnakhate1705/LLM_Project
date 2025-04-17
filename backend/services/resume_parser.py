import os
from PyPDF2 import PdfReader

def extract_resume_text(pdf_file_stream) -> str:
    """
    Extracts text from a PDF file stream (from request.files['file']).

    Args:
        pdf_file_stream: FileStorage object from Flask (request.files)

    Returns:
        str: Extracted text from all PDF pages
    """
    reader = PdfReader(pdf_file_stream)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()
