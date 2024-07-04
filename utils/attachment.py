from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st
import PyPDF2

def generate_attachment(analysis):
    # Define the prompt to generate attachment content based on the analysis
    prompt = f"Generate an attachment content based on the following analysis:\n\n{analysis}"
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0)
    
    prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = prompt_template | chat_model
    
    attachment_content = chain.invoke({"text": analysis}).content
    
    # Create a PDF file with the generated content
    pdf_buffer = io.BytesIO()
    pdf_writer = PyPDF2.PdfWriter()
    
    pdf_writer.add_page(PDFPage.create_text_page(attachment_content))
    
    pdf_writer.write(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()
