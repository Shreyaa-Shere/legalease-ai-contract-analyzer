"""
Text Extraction Utility Module

This module contains functions to extract text from PDF and DOCX files.
Think of this as a "translator" that reads contract files and extracts the text content.

BEGINNER EXPLANATION:
--------------------
When you upload a contract file (PDF or DOCX), the computer needs to:
1. Read the file
2. Extract all the text from it
3. Store that text in our database

PDF files and DOCX files are like books - they have text, but they're stored
in a special format. We need special "readers" (libraries) to extract the text.

This module uses:
- PyPDF2: Library to read PDF files (like Adobe Reader, but for code)
- python-docx: Library to read DOCX files (like Microsoft Word, but for code)
"""

import logging
from pathlib import Path

# Import libraries for reading files
try:
    import PyPDF2  # For reading PDF files
except ImportError:
    PyPDF2 = None
    logging.warning("PyPDF2 not installed. PDF text extraction will not work.")

try:
    from docx import Document  # For reading DOCX files
except ImportError:
    Document = None
    logging.warning("python-docx not installed. DOCX text extraction will not work.")

# Set up logging (this helps us see errors if something goes wrong)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.
    
    BEGINNER EXPLANATION:
    ---------------------
    PDF (Portable Document Format) files are like digital books.
    They contain text, images, and formatting, but the text is "embedded" 
    in a special way that's hard to read directly.
    
    PyPDF2 is a library that knows how to "read" PDFs and extract the text.
    
    HOW IT WORKS:
    1. Open the PDF file
    2. Read each page one by one
    3. Extract text from each page
    4. Combine all pages into one big text string
    5. Return the text
    
    PARAMETERS:
    -----------
    file_path: str or Path
        The full path to the PDF file on the server's disk
        Example: "/path/to/media/contracts/2024/01/15/contract.pdf"
    
    RETURNS:
    --------
    str: The extracted text from all pages of the PDF
         Returns empty string "" if extraction fails
    
    EXAMPLE:
    --------
    text = extract_text_from_pdf("/path/to/contract.pdf")
    print(text)  # Prints all text from the PDF
    """
    
    # Check if PyPDF2 is available
    if PyPDF2 is None:
        logger.error("PyPDF2 library is not installed. Cannot extract text from PDF.")
        return ""
    
    try:
        # Open the PDF file in read-binary mode ('rb')
        # 'rb' means "read binary" - PDFs are binary files, not plain text
        with open(file_path, 'rb') as file:
            # Create a PDF reader object
            # This is like opening the PDF in a PDF reader program
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Initialize empty string to store all text
            extracted_text = ""
            
            # Get the number of pages in the PDF
            num_pages = len(pdf_reader.pages)
            logger.info(f"Extracting text from PDF with {num_pages} pages")
            
            # Loop through each page
            # Pages are numbered starting from 0 (0, 1, 2, 3...)
            for page_num in range(num_pages):
                # Get the specific page
                page = pdf_reader.pages[page_num]
                
                # Extract text from this page
                page_text = page.extract_text()
                
                # Add the page text to our collected text
                # We add "\n\n" (two newlines) between pages for readability
                extracted_text += page_text
                
                # Add page separator if not the last page
                if page_num < num_pages - 1:
                    extracted_text += "\n\n--- Page {} ---\n\n".format(page_num + 1)
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
            return extracted_text
            
    except Exception as e:
        # If anything goes wrong, log the error and return empty string
        # This way, the rest of our app doesn't crash if a PDF is corrupted
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""


def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX (Word) file.
    
    BEGINNER EXPLANATION:
    ---------------------
    DOCX is Microsoft Word's file format. Like PDFs, it stores text in a special way.
    
    python-docx is a library that can "read" DOCX files and extract the text.
    
    HOW IT WORKS:
    1. Open the DOCX file
    2. Read all paragraphs (paragraphs are like paragraphs in Word)
    3. Extract text from each paragraph
    4. Combine all paragraphs into one text string
    5. Return the text
    
    PARAMETERS:
    -----------
    file_path: str or Path
        The full path to the DOCX file on the server's disk
        Example: "/path/to/media/contracts/2024/01/15/contract.docx"
    
    RETURNS:
    --------
    str: The extracted text from all paragraphs in the DOCX
         Returns empty string "" if extraction fails
    
    EXAMPLE:
    --------
    text = extract_text_from_docx("/path/to/contract.docx")
    print(text)  # Prints all text from the DOCX
    """
    
    # Check if python-docx is available
    if Document is None:
        logger.error("python-docx library is not installed. Cannot extract text from DOCX.")
        return ""
    
    try:
        # Open the DOCX file using the Document class
        # This is like opening the file in Microsoft Word
        doc = Document(file_path)
        
        # Initialize empty list to store paragraph texts
        paragraphs = []
        
        # Loop through each paragraph in the document
        # In Word documents, text is organized into paragraphs
        for paragraph in doc.paragraphs:
            # Get the text from this paragraph
            paragraph_text = paragraph.text.strip()  # .strip() removes extra spaces
            
            # Only add non-empty paragraphs (skip blank lines)
            if paragraph_text:
                paragraphs.append(paragraph_text)
        
        # Join all paragraphs with double newlines
        # This creates a nice readable text with spacing between paragraphs
        extracted_text = "\n\n".join(paragraphs)
        
        logger.info(f"Successfully extracted {len(extracted_text)} characters from DOCX")
        return extracted_text
        
    except Exception as e:
        # If anything goes wrong, log the error and return empty string
        logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
        return ""


def extract_text_from_file(file_path, file_type):
    """
    Main function to extract text from any supported file type.
    
    BEGINNER EXPLANATION:
    ---------------------
    This is a "smart" function that automatically chooses the right extraction method
    based on the file type. It's like having a smart assistant who knows:
    - "Oh, this is a PDF? Use the PDF reader!"
    - "Oh, this is a DOCX? Use the DOCX reader!"
    
    HOW IT WORKS:
    1. Check the file type (PDF or DOCX)
    2. Call the appropriate extraction function
    3. Return the extracted text
    
    PARAMETERS:
    -----------
    file_path: str or Path
        The full path to the file on the server's disk
    
    file_type: str
        The type of file: 'pdf' or 'docx'
        This tells us which extraction method to use
    
    RETURNS:
    --------
    str: The extracted text from the file
         Returns empty string "" if extraction fails or file type is unsupported
    
    EXAMPLE:
    --------
    text = extract_text_from_file("/path/to/contract.pdf", "pdf")
    text = extract_text_from_file("/path/to/contract.docx", "docx")
    """
    
    # Convert file_path to Path object if it's a string
    # Path objects make it easier to work with file paths
    file_path = Path(file_path)
    
    # Check if the file actually exists
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return ""
    
    # Use lowercase file type for comparison (case-insensitive)
    file_type_lower = file_type.lower()
    
    # Choose the right extraction method based on file type
    if file_type_lower == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type_lower == 'docx':
        return extract_text_from_docx(file_path)
    else:
        # Unsupported file type
        logger.warning(f"Unsupported file type for text extraction: {file_type}")
        return ""

