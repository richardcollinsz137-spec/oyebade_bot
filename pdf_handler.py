import io
import logging
import pdfplumber
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Attempts programmatic text layer extraction. 
    If extracted text is virtually non-existent, it flags the PDF 
    as an image-based/scanned file and redirects to the OCR engine.
    """
    extracted_text = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_text.append(page_text)
        
        full_text = "\n".join(extracted_text).strip()
        
        # Threshold Check: If under 15 characters, fall back to OCR
        if len(full_text) > 15:
            logger.info("Native digital text layer extracted successfully.")
            return full_text
            
        logger.info("Digital text layers missing or insufficient. Routing to Tesseract OCR...")
        return run_ocr_fallback(file_path)

    except Exception as e:
        logger.error(f"Error inside processing module execution path: {str(e)}", exc_info=True)
        raise RuntimeError("Failed to correctly parse PDF internal structure.")

def run_ocr_fallback(file_path: str) -> str:
    """Renders vector PDF layout pages to bitmap images and runs Tesseract text extraction."""
    ocr_text = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                logger.info(f"Running Optical Character Recognition on page {page_index}...")
                
                # Render vector objects to 200 DPI bitmap target
                image_rendering = page.to_image(resolution=200)
                image_stream = io.BytesIO()
                image_rendering.save(image_stream, format="PNG")
                image_stream.seek(0)
                
                # Send memory image directly to pytesseract
                pil_image = Image.open(image_stream)
                page_ocr_result = pytesseract.image_to_string(pil_image)
                
                if page_ocr_result.strip():
                    ocr_text.append(page_ocr_result)
                    
        return "\n".join(ocr_text).strip()
    except Exception as e:
        logger.error(f"Critical error down the OCR pipeline path: {str(e)}")
        raise RuntimeError("OCR processing failed due to external execution fault.")
