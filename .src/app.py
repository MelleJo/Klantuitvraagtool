import streamlit as st
from openai import OpenAI
import pyperclip
from docx import Document
from io import BytesIO
from email_generator import generate_email_body
from smart_analyzer import analyze_product_info_and_risks
from audio_processing import process_audio_input, transcribe_audio
import tempfile

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_insurance_products():
    # In a real application, this would load from a database or file
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
    st.set_page_config(page_title="Verzekeringsadviseur E-mail Generator", layout="wide")
    
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
        if st.button("Start Audio Opname"):
            transcript = process_audio_input()
            if transcript:
                st.session_state['transcript'] = transcript
                st.success("Transcriptie voltooid!")
    else:  # Upload audio
        uploaded_file = st.file_uploader("Upload een audiobestand", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
        if uploaded_file is not None:
            if st.button("Transcribeer Geüpload Bestand"):
                with st.spinner("Transcriberen van audio..."):
                    audio_bytes = uploaded_file.read()
                    st.session_state['transcript'] = transcribe_audio(audio_bytes)
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