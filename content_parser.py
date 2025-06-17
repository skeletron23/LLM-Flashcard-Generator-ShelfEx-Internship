# content_parser.py
import io
from pypdf import PdfReader
from typing import Optional

def load_text_from_txt(file_obj: io.BytesIO) -> str:
    """Reads text content from a .txt file object."""
    return file_obj.read().decode('utf-8')

def load_text_from_pdf(file_obj: io.BytesIO) -> str:
    """Reads text content from a .pdf file object."""
    reader = PdfReader(file_obj)
    text = ""
    for page in reader.pages:
        # .extract_text() can return None for empty pages, so handle it
        text += page.extract_text() or ""
    return text

def parse_input_content(input_type: str, file_obj: Optional[io.BytesIO] = None, direct_text: Optional[str] = None) -> str:
    """
    Parses educational content based on the input type.

    Args:
        input_type (str): 'file_upload' or 'direct_paste'. 
        file_obj (io.BytesIO, optional): File object for file uploads (.txt, .pdf). 
        direct_text (str, optional): Raw text for direct paste. 

    Returns:
        str: The extracted text content.
    """
    if input_type == 'file_upload':
        if file_obj:
            if file_obj.name.endswith('.txt'):
                return load_text_from_txt(file_obj)
            elif file_obj.name.endswith('.pdf'):
                return load_text_from_pdf(file_obj)
            else:
                raise ValueError("Unsupported file type. Only .txt and .pdf are supported.")
        else:
            raise ValueError("No file uploaded for file_upload type.")
    elif input_type == 'direct_paste':
        if direct_text:
            return direct_text
        else:
            raise ValueError("No text provided for direct_paste type.")
    else:
        raise ValueError("Invalid input type specified.")