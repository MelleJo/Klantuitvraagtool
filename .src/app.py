import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import tempfile
from datetime import datetime
import pytz
import pyperclip
from pydub import AudioSegment
import io
import os
from email_generator import generate_email_body
from smart_analyzer import analyze_product_info_and_risks
import ffmpeg
import tempfile

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state variables
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = ""
if 'email_body' not in st.session_state:
    st.session_state['email_body'] = ""
if 'product_info' not in st.session_state:
    st.session_state['product_info'] = ""

def get_local_time():
    timezone = pytz.timezone("Europe/Amsterdam")
    return datetime.now(timezone).strftime('%d-%m-%Y %H:%M:%S')

def split_audio(audio_bytes, max_duration_ms=30000):
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
    chunks = []
    for i in range(0, len(audio), max_duration_ms):
        chunks.append(audio[i:i+max_duration_ms])
    return chunks

def transcribe_audio(audio_bytes):
    transcript_text = ""
    with st.spinner('Audio transcriptie wordt uitgevoerd...'):
        try:
            audio_segments = split_audio(audio_bytes)
        except Exception as e:
            st.error(f"Fout bij het segmenteren van het audio: {str(e)}")
            return "Segmentatie mislukt."

        total_segments = len(audio_segments)
        progress_bar = st.progress(0)
        progress_text = st.empty()
        progress_text.text("Start transcriptie...")
        for i, segment in enumerate(audio_segments):
            progress_text.text(f'Bezig met verwerken van segment {i+1} van {total_segments} - {((i+1)/total_segments*100):.2f}% voltooid')
            with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as temp_file:
                segment.export(temp_file.name, format="wav")
                with open(temp_file.name, "rb") as audio_file:
                    try:
                        transcription_response = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
                        if hasattr(transcription_response, 'text'):
                            transcript_text += transcription_response.text + " "
                    except Exception as e:
                        st.error(f"Fout bij het transcriberen: {str(e)}")
                        continue
            progress_bar.progress((i + 1) / total_segments)
        progress_text.success("Transcriptie voltooid.")
    return transcript_text.strip()

def main():
    st.set_page_config(page_title="Slimme Verzekeringsadviseur E-mail Generator", layout="wide")
    
    st.title("Slimme Verzekeringsadviseur E-mail Generator")
    
    api_key = st.secrets["OPENAI_API_KEY"]
    if not api_key:
        st.error("OpenAI API-sleutel niet gevonden. Controleer uw Streamlit Secrets.")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Audio Opname")
        audio_data = mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True, format="webm")
        
        if audio_data and 'bytes' in audio_data:
            st.audio(audio_data['bytes'])
            if st.button("Transcribeer Audio"):
                st.session_state['transcript'] = transcribe_audio(audio_data['bytes'])
                st.success("Audio getranscribeerd!")

        st.subheader("Transcript")
        if 'transcript' in st.session_state:
            st.session_state['transcript'] = st.text_area("Bewerk transcript indien nodig", value=st.session_state['transcript'], height=200)

        if st.button("Analyseer en Genereer E-mail"):
            if st.session_state['transcript']:
                try:
                    # Analyze product info and risks
                    product_analysis = analyze_product_info_and_risks(st.session_state['transcript'], api_key)
                    st.session_state['product_info'] = product_analysis

                    # Generate email body
                    st.session_state['email_body'] = generate_email_body(st.session_state['transcript'], api_key)
                    
                    st.success("Analyse voltooid en e-mailtekst gegenereerd!")
                except Exception as e:
                    st.error(f"Er is een fout opgetreden: {str(e)}")
            else:
                st.warning("Transcribeer eerst de audio of voer handmatig een transcript in.")

    with col2:
        st.subheader("AI Verzekeringsadviseur Analyse")
        if 'product_info' in st.session_state and st.session_state['product_info']:
            st.text_area("Productinformatie en Risico-analyse", value=st.session_state['product_info'], height=200)
            
            # Parse the product_info to get the list of products for the attachment
            products_for_attachment = st.session_state['product_info'].split("Aanbevolen bijlage-inhoud:")[1].split("Ontbrekende cruciale verzekeringen:")[0].strip()
            products_list = [product.strip() for product in products_for_attachment.split(",")]
            
            st.subheader("Bevestig Bijlage-inhoud")
            selected_products = st.multiselect("Selecteer producten voor de bijlage", products_list, default=products_list)
            
            if st.button("Genereer Bijlage"):
                # Here you would generate the attachment based on selected_products
                st.success("Bijlage gegenereerd! (Implementatie vereist)")

        st.subheader("Gegenereerde E-mailtekst")
        if 'email_body' in st.session_state and st.session_state['email_body']:
            st.text_area("E-mailtekst", value=st.session_state['email_body'], height=300)
            if st.button("Kopieer naar Klembord"):
                pyperclip.copy(st.session_state['email_body'])
                st.success("E-mailtekst gekopieerd naar klembord!")

if __name__ == "__main__":
    main()