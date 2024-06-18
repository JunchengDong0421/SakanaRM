from PyPDF2 import PdfReader


def read_pdf_texts(file_obj):
    reader = PdfReader(file_obj)
    # Check if the PDF is encrypted
    if reader.is_encrypted:
        reader.decrypt('')

    text_content = []
    # Iterate through all the pages
    for page in reader.pages:
        text_content.append(page.extract_text())

    return " ".join(text_content)
