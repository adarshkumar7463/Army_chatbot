# main/ocr_utils.py
import pytesseract
import cv2
import numpy as np
import re
import os
from PIL import Image
import tempfile
import logging
import io

logger = logging.getLogger(__name__)


# Set Tesseract path for Windows 
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'

# ocr_utils.py
def preprocess_image(image):
    """Robust image preprocessing pipeline"""
    try:
        # Convert to OpenCV format
        if isinstance(image, Image.Image):
            img = np.array(image)
            if len(img.shape) == 2:  # Grayscale
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif img.shape[2] == 4:  # RGBA
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            else:  # RGB
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            img = image
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize if too large
        height, width = gray.shape
        if max(height, width) > 2000:
            scale = 2000 / max(height, width)
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        
        # Remove shadows
        dilated = cv2.dilate(gray, np.ones((7, 7), np.uint8))
        blurred = cv2.medianBlur(dilated, 21)
        diff = 255 - cv2.absdiff(gray, blurred)
        normalized = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(normalized)
        
        # Binarization
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)
        
        return denoised
        
    except Exception as e:
        logger.error(f"Preprocessing error: {str(e)}")
        return image
# ocr_utils.py
def extract_fields(file):
    """Extract fields and full text from document"""
    try:
        # Read file content
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Open image
        image = Image.open(io.BytesIO(file_content))
        
        # Preprocess image
        processed_img = preprocess_image(image)
        
        # Perform OCR to get full text
        full_text = pytesseract.image_to_string(processed_img, lang='eng')
        
        # Basic field extraction
        extracted_data = {
            'army_number': extract_value(full_text, 'army number', 'id'),
            'full_name': extract_value(full_text, 'name', 'full name'),
            'rank': extract_value(full_text, 'rank'),
            'position': extract_value(full_text, 'position', 'post'),
            'unit': extract_value(full_text, 'unit'),
            'dob': extract_date(full_text),
            'enlistment_date': extract_date(full_text, 'enlistment'),
            'phone': extract_phone(full_text),
            'email': extract_email(full_text),
            'blood_group': extract_blood_group(full_text),
            'address': extract_address(full_text),
            'full_text': full_text  # Add full extracted text
        }
        
        return extracted_data
        
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        return {"error": str(e)}

def extract_simple(text, *keywords):
    """Extract value after keywords"""
    text = text.lower()
    for keyword in keywords:
        idx = text.find(keyword)
        if idx != -1:
            # Extract text after keyword
            value_start = idx + len(keyword)
            value_text = text[value_start:value_start+100].split('\n')[0]
            # Clean and return
            return value_text.strip(":;. \t").upper()
    return ""

def extract_date(text, keyword=None):
    """Extract date value"""
    # If keyword is provided, try to extract after keyword
    if keyword:
        result = extract_value(text, keyword)
        if result:
            return result
    
    # Fallback to date pattern
    dates = re.findall(r'\d{2}[/-]\d{2}[/-]\d{4}', text)
    return dates[0] if dates else ""

def extract_phone(text):
    """Extract phone number"""
    phones = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    return phones[0] if phones else ""

def extract_email(text):
    """Extract email address"""
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return emails[0] if emails else ""
def extract_blood_group(text):
    """Extract blood group"""
    groups = re.findall(r'\b([ABO][+\-])\b', text, re.IGNORECASE)
    return groups[0].upper() if groups else ""

def extract_address(text):
    """Simple address extraction"""
    # Look for multi-line text block
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'address' in line.lower():
            # Return next 2-3 lines as address
            address_lines = lines[i+1:i+4]
            return ', '.join([l.strip() for l in address_lines if l.strip()])
    return ""
    
from .ocr_utils import extract_fields
from PIL import Image
from django.http import JsonResponse

def extract_officer_data(request):
    try:
        file = request.FILES['image']
        image = Image.open(file)
        debug_dir = 'debug_images'  # optional

        extracted_data = extract_fields(image, debug_dir)

        if not extracted_data:
            return JsonResponse({'error': 'OCR failed'})

        return JsonResponse(extracted_data)

    except Exception as e:
        print("OCR processing error")
        print(e)
        return JsonResponse({'error': str(e)}) 
    
def extract_value(text, *keywords):
    """Extract value after keywords"""
    text = text.lower()
    for keyword in keywords:
        idx = text.find(keyword)
        if idx != -1:
            # Extract text after keyword
            value_start = idx + len(keyword)
            value_text = text[value_start:value_start+100].split('\n')[0]
            # Clean and return
            return value_text.strip(":;. \t").title()
    return ""