from utils.api_calls import generate_attachment_api
import io
import PyPDF2

def generate_attachment(analysis):
    attachment_content = generate_attachment_api(analysis)
    
    # Create a PDF file with the generated content
    pdf_buffer = io.BytesIO()
    pdf_writer = PyPDF2.PdfWriter()
    
    pdf_writer.add_page(PDFPage.create_text_page(attachment_content))
    
    pdf_writer.write(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()
