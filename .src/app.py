import streamlit as st

# Ensure set_page_config is the very first Streamlit command
st.set_page_config(page_title="Verzekeringsadviseur E-mail Generator", layout="wide")

from openai import OpenAI
import pyperclip
from docx import Document
import sys
import os

# Add the src directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.src')))

import audio_processing  # Ensure correct import path
st.write(f"Debug: Imported audio_processing module with functions: {dir(audio_processing)}")

from io import BytesIO
from email_generator import generate_email_body
from smart_analyzer import analyze_product_info_and_risks
import tempfile

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_insurance_products():
    return [
        "Aansprakelijkheidsverzekering",
        "Bedrijfsschadeverzekering",
        "Cyberverzekering",
        "Rechtsbijstandverzekering",
        "Bestuurdersaansprakelijkheidsverzekering"
    ]

def create_docx_attachment(products):
    doc = Document()
    doc.add_heading('Productinformatie en Risico\'s', 0)
    
    for product in products:
        doc.add_heading(product, level=1)
        doc.add_paragraph('Hier komt gedetailleerde informatie over het product en de bijbehorende risico\'s.')
        doc.add_paragraph('Deze informatie zou in een echte applicatie uit een database of API worden gehaald.')
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def main():
    st.title("Verzekeringsadviseur E-mail Generator")
    
    if 'transcript' not in st.session_state:
        st.session_state['transcript'] = ""
    if 'email_body' not in st.session_state:
        st.session_state['email_body'] = ""
    if 'product_info' not in st.session_state:
        st.session_state['product_info'] = {}

    # Step 1: Choose input method
    st.subheader("1. Kies een invoermethode")
    input_method = st.radio("Hoe wil je de audio invoeren?", ["Neem audio op", "Upload audio"])

    # Step 2: Record or Upload audio
    st.subheader("2. Voer audio in")
    if input_method == "Neem audio op":
        st.write("Debug: Attempting to record audio")
        audio_data = audio_processing.record_audio()
        st.write(f"Debug: record_audio returned {type(audio_data)}")
        if audio_data and isinstance(audio_data, dict) and 'bytes' in audio_data:
            st.audio(audio_data['bytes'], format="audio/wav")
            if st.button("Transcribeer Opgenomen Audio"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                    tmp_audio.write(audio_data['bytes'])
                    tmp_audio.flush()
                    st.session_state['transcript'] = audio_processing.transcribe_audio(tmp_audio.name)
                st.success("Transcriptie voltooid!")
    else:
        st.write("Debug: Attempting to upload audio")
        uploaded_file = audio_processing.upload_audio()
        st.write(f"Debug: upload_audio returned {type(uploaded_file)}")
        if uploaded_file is not None:
            st.audio(uploaded_file, format=f"audio/{uploaded_file.type.split('/')[-1]}")
            if st.button("Transcribeer Geüpload Bestand"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.type.split('/')[-1]}") as tmp_audio:
                    tmp_audio.write(uploaded_file.getvalue())
                    tmp_audio.flush()
                    st.session_state['transcript'] = audio_processing.transcribe_audio(tmp_audio.name)
                st.success("Transcriptie voltooid!")

    # Step 3: Display and edit transcript
    if st.session_state['transcript']:
        st.subheader("3. Bekijk en bewerk het transcript")
        st.session_state['transcript'] = st.text_area("Bewerk transcript indien nodig", value=st.session_state['transcript'], height=200)
        
        # Step 4: Get AI suggestions
        if st.button("Analyseer Transcript"):
            with st.spinner("Bezig met analyseren..."):
                st.session_state['product_info'] = analyze_product_info_and_risks(st.session_state['transcript'], st.secrets["OPENAI_API_KEY"])
            st.success("Analyse voltooid!")

    # Step 5: Choose products
    if st.session_state['product_info']:
        st.subheader("4. Kies producten voor de bijlage")
        st.json(st.session_state['product_info'])
        
        recommended_products = st.session_state['product_info'].get('aanbevolen_bijlage_inhoud', [])
        all_products = load_insurance_products()
        default_selection = list(set(recommended_products) & set(all_products))
        
        selected_products = st.multiselect(
            "Selecteer producten voor de bijlage",
            options=all_products,
            default=default_selection
        )
        
        custom_product = st.text_input("Voeg een eigen product toe")
        if custom_product:
            selected_products.append(custom_product)

        # Step 6: Generate email and attachment
        if st.button("Genereer E-mail en Bijlage"):
            with st.spinner("Bezig met genereren van e-mail en bijlage..."):
                st.session_state['email_body'] = generate_email_body(st.session_state['transcript'], st.secrets["OPENAI_API_KEY"])
                attachment = create_docx_attachment(selected_products)
            
            st.subheader("5. Gegenereerde E-mailtekst")
            st.text_area("E-mailtekst", value=st.session_state['email_body'], height=300)
            
            if st.button("Kopieer naar Klembord"):
                pyperclip.copy(st.session_state['email_body'])
                st.success("E-mailtekst gekopieerd naar klembord!")
            
            st.download_button(
                label="Download Bijlage",
                data=attachment,
                file_name="productinformatie.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main()
