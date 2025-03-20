import re
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
           # text = re.sub(r'[^\x20-\x7E]', '', text)  # optional remove non-printable characters.
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    
if __name__ == '__main__':
    pdf_file = "../knowledge/Алексеев, Панин. Философия.pdf"  # Replace with your PDF file

    extracted_text = extract_text_from_pdf(pdf_file)

    if extracted_text:
        print("Extracted Text:\n", extracted_text)
        print(len(extracted_text))
    else:
        print("Text extraction failed.")