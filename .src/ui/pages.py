import streamlit as st
import simplejson as json
from ui.components import (
    display_input_method_selector,
    display_text_input,
    display_file_uploader,
    display_generate_button,
    display_progress_bar,
    display_spinner,
    display_success,
    display_error,
    display_warning,
    display_metric   
)
from utils.audio_processing import transcribe_audio, process_audio_input
from utils.file_processing import process_uploaded_file
from services.summarization_service import analyze_transcript, generate_email_wrapper
from services.email_service import send_feedback_email
from autogen_agents import correction_AI
import os
import html
import time
from utils.session_state import update_session_state, move_to_step, clear_analysis_results
import logging
from typing import List, Dict, Any
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

import os
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_available_insurances(analysis_result: Dict[str, Any]) -> List[str]:
    try:
        # Get the absolute path to the current file
        current_file_path = os.path.abspath(__file__)
        st.write(f"Current file path: {current_file_path}")
        
        # Navigate to the project root (assuming 'pages.py' is in 'src/ui/')
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        st.write(f"Project root: {project_root}")
        
        # Construct the path to the insurance_guidelines directory
        guidelines_dir = os.path.join(project_root, '.src', 'insurance_guidelines')
        st.write(f"Guidelines directory: {guidelines_dir}")
        
        if not os.path.exists(guidelines_dir):
            st.error(f"The directory {guidelines_dir} does not exist.")
            raise FileNotFoundError(f"The directory {guidelines_dir} does not exist.")
        
        available_files = [f.split('.')[0] for f in os.listdir(guidelines_dir) if f.endswith('.txt')]
        st.write(f"Available insurance types: {available_files}")
        
        # Prepare the analysis content
        analysis_content = json.dumps(analysis_result, ensure_ascii=False)
        
        # Use GPT-4o-mini to identify relevant insurances
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that identifies relevant insurance types from an analysis."},
                {"role": "user", "content": f"Given the following analysis result, identify the relevant insurance types from this list: {', '.join(available_files)}. Respond with only the relevant insurance types, separated by commas.\n\nAnalysis:\n{analysis_content}"}
            ],
            temperature=0.2,
            max_tokens=100
        )
        
        identified_insurances = [ins.strip() for ins in response.choices[0].message.content.split(',')]
        return [ins for ins in identified_insurances if ins in available_files]
    
    except Exception as e:
        logging.error(f"Error in get_available_insurances: {str(e)}")
        st.error(f"Er is een fout opgetreden bij het ophalen van de beschikbare verzekeringen: {str(e)}")
        return []



def render_input_step(config):
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📝 Gegevens invoeren")
    input_method = st.selectbox("Selecteer invoermethode:", config["INPUT_METHODS"])

    if input_method == "Upload audiobestand":
        uploaded_file = st.file_uploader("Upload een audiobestand", type=["wav", "mp3", "m4a", "ogg", "weba", "mp4"])
        if uploaded_file is not None:
            st.info("Audiobestand geüpload. Transcriptie wordt gestart...")
            with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                audio_file_path = process_audio_input(input_method, uploaded_file)
                if audio_file_path:
                    transcript = transcribe_audio(audio_file_path)
                    update_session_state('transcript', transcript)
                    update_session_state('input_processed', True)
                    update_session_state('transcription_complete', True)
                    st.success("Audio succesvol verwerkt en getranscribeerd!")

    elif input_method == "Neem audio op":
        audio_file_path = process_audio_input(input_method)
        if audio_file_path:
            with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                transcript = transcribe_audio(audio_file_path)
                update_session_state('transcript', transcript)
                update_session_state('input_processed', True)
                update_session_state('transcription_complete', True)
            st.success("Audio succesvol opgenomen en getranscribeerd!")

    elif input_method == "Upload tekstbestand":
        uploaded_file = st.file_uploader("Upload een bestand:", type=['txt', 'docx', 'pdf'])
        if uploaded_file is not None:
            st.info("Bestand geüpload. Verwerking wordt gestart...")
            with st.spinner("Bestand wordt verwerkt..."):
                transcript = process_uploaded_file(uploaded_file)
                update_session_state('transcript', transcript)
                update_session_state('input_processed', True)
                update_session_state('transcription_complete', True)
            st.success("Bestand succesvol geüpload en verwerkt!")

    elif input_method == "Voer tekst in of plak tekst":
        input_text = st.text_area("Voer tekst in of plak tekst:", height=200, key="input_text_area")
        if st.button("Verwerk tekst"):
            if input_text:
                update_session_state('transcript', input_text)
                update_session_state('input_processed', True)
                update_session_state('transcription_complete', True)
                st.success("Tekst succesvol verwerkt!")
            else:
                st.warning("Voer eerst tekst in voordat u op 'Verwerk tekst' klikt.")

    if st.session_state.get('transcription_complete', False):
        st.markdown("### 📄 Gegenereerd transcript")
        st.text_area("", value=st.session_state.get('transcript', ''), height=200, key="transcript_display", disabled=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_analysis_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("🔍 Analyseresultaten")
    
    if not st.session_state.get('analysis_complete', False):
        with st.spinner("Transcript wordt geanalyseerd..."):
            try:
                analysis_result = analyze_transcript(st.session_state.get('transcript', ''))
                if "error" in analysis_result:
                    raise Exception(analysis_result["error"])
                update_session_state('suggestions', analysis_result)
                update_session_state('analysis_complete', True)
                st.success("Analyse succesvol afgerond!")
            except Exception as e:
                st.error(f"Er is een fout opgetreden tijdens de analyse: {str(e)}")
                st.stop()

    if st.session_state.get('analysis_complete', False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Huidige dekking")
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            current_coverage = st.session_state.get('suggestions', {}).get('current_coverage', [])
            if current_coverage:
                for coverage in current_coverage:
                    st.write(f"• {coverage}")
            else:
                st.write("Geen huidige dekking geïdentificeerd.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ⚠️ Geïdentificeerde risico's")
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            identified_risks = st.session_state.get('suggestions', {}).get('coverage_gaps', [])
            if identified_risks:
                for risk in identified_risks:
                    st.write(f"• {risk}")
            else:
                st.write("Geen specifieke risico's geïdentificeerd.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def on_generate_client_report():
    move_to_step(4)

def render_recommendations_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("💡 Aanbevelingen")

    if 'suggestions' not in st.session_state or not st.session_state.get('suggestions'):
        st.warning("Geen aanbevelingen beschikbaar. Voer eerst de analysestap uit.")
    else:
        analysis_result = st.session_state.get('suggestions', {})
        recommendations = analysis_result.get('recommendations', [])
        
        if not recommendations:
            st.warning("Er zijn geen aanbevelingen gegenereerd in de analysestap.")
        else:
            st.write("Selecteer de aanbevelingen die u wilt opnemen in het klantrapport:")

            selected_recommendations = []
            for i, rec in enumerate(recommendations):
                if st.checkbox(rec.get('title', f"Aanbeveling {i+1}"), key=f"rec_checkbox_{i}"):
                    selected_recommendations.append(rec)

                with st.expander(f"Details voor {rec.get('title', f'Aanbeveling {i+1}')}", expanded=False):
                    st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
                    if 'description' in rec:
                        st.markdown(f'<p class="recommendation-title">Beschrijving:</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="recommendation-content">{rec["description"]}</p>', unsafe_allow_html=True)
                    if 'rechtvaardiging' in rec:
                        st.markdown(f'<p class="recommendation-title">Rechtvaardiging:</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="recommendation-content">{rec["rechtvaardiging"]}</p>', unsafe_allow_html=True)
                    if 'specific_risks' in rec and rec['specific_risks']:
                        st.markdown('<p class="recommendation-title">Specifieke risico\'s:</p>', unsafe_allow_html=True)
                        st.markdown('<ul class="recommendation-list">', unsafe_allow_html=True)
                        for risk in rec['specific_risks']:
                            st.markdown(f'<li>{risk}</li>', unsafe_allow_html=True)
                        st.markdown('</ul>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            update_session_state('selected_suggestions', selected_recommendations)
            st.success(f"{len(selected_recommendations)} aanbevelingen geselecteerd.")

            # Identify relevant insurances
            identified_insurances = get_available_insurances(analysis_result)

            # Add insurance type checklist
            st.subheader("Geïdentificeerde verzekeringen")
            if identified_insurances:
                for insurance in identified_insurances:
                    st.checkbox(insurance.capitalize(), value=True, key=f"insurance_checkbox_{insurance}")
            else:
                st.info("Geen specifieke verzekeringen geïdentificeerd. Controleer de analyse of voeg handmatig toe.")

            # Add dropdown to include additional insurances
            additional_insurance = st.text_input(
                "Voeg een extra verzekering toe (optioneel)",
                key="additional_insurance_input"
            )
            if additional_insurance:
                identified_insurances.append(additional_insurance)

            update_session_state('identified_insurances', identified_insurances)

            if selected_recommendations:
                if st.button("Genereer klantrapport"):
                    st.session_state.active_step = 4
            else:
                st.info("Selecteer ten minste één aanbeveling om een klantrapport te genereren.")

    st.markdown("</div>", unsafe_allow_html=True)
    
from services.summarization_service import generate_email_wrapper

from utils.text_processing import load_guidelines  # Add this import at the top of the file

def render_client_report_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📄 Klantrapport")

    if 'email_content' not in st.session_state or not st.session_state.get('email_content'):
        if st.button("Genereer klantrapport"):
            with st.spinner("Rapport wordt gegenereerd..."):
                try:
                    transcript = st.session_state.get('transcript', '')
                    suggestions = st.session_state.get('suggestions', {})
                    selected_suggestions = st.session_state.get('selected_suggestions', [])
                    identified_insurances = st.session_state.get('identified_insurances', [])

                    current_coverage = suggestions.get('current_coverage', [])
                    enhanced_coverage = [{"title": item, "coverage": item} for item in current_coverage]

                    # Step 1: Generate the email content
                    email_content = generate_email_wrapper(
                        transcript=transcript,
                        enhanced_coverage=enhanced_coverage,
                        selected_recommendations=selected_suggestions,
                        identified_insurances=identified_insurances
                    )

                    if not email_content:
                        raise ValueError("Email generator did not return any content.")

                    # Step 2: Apply the Correction AI
                    st.info("Correcting email text...")
                    guidelines = load_guidelines()  # Load the general guidelines
                    corrected_email_content = correction_AI(email_content, guidelines)

                    # Step 3: Update the session state with the corrected content
                    update_session_state('email_content', corrected_email_content)

                    st.success("Klantrapport succesvol gegenereerd en gecorrigeerd!")
                    st.rerun()

                except Exception as e:
                    logger.error(f"Error in render_client_report_step: {str(e)}")
                    st.error(f"Er is een fout opgetreden bij het genereren van het rapport: {str(e)}")
                    st.stop()

    if st.session_state.get('email_content'):
        st.markdown("### 📥 Rapportinhoud")
        st.markdown(st.session_state.get('email_content', ''), unsafe_allow_html=True)

        st.download_button(
            label="Download rapport",
            data=st.session_state.get('email_content', ''),
            file_name="VerzekeringRapport_Klant.md",
            mime="text/markdown"
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_conversation_history():
    st.subheader("Laatste vijf gesprekken")
    gesprekslog = st.session_state.get('gesprekslog', [])
    if not gesprekslog:
        st.info("Er zijn nog geen gesprekken opgeslagen.")
    else:
        for i, gesprek in enumerate(gesprekslog):
            with st.expander(f"Gesprek {i+1} op {gesprek.get('time', 'Onbekende tijd')}"):
                st.markdown("**Transcript:**")
                st.markdown(f'<div class="content">{html.escape(gesprek.get("transcript", ""))}</div>', unsafe_allow_html=True)
                st.markdown("**Gegenereerde e-mail:**")
                st.markdown(f'<div class="content">{gesprek.get("klantuitvraag", "")}</div>', unsafe_allow_html=True)
    

def render_feedback_form():
    with st.form(key="feedback_form"):
        user_first_name = st.text_input("Uw voornaam (verplicht bij feedback):")
        feedback = st.radio("Was deze klantuitvraag nuttig?", ["Positief", "Negatief"])
        additional_feedback = st.text_area("Laat aanvullende feedback achter:")
        submit_button = st.form_submit_button(label="Verzend feedback")

        if submit_button:
            if not user_first_name:
                st.warning("Voornaam is verplicht bij het geven van feedback.", icon="⚠️")
            else:
                success = send_feedback_email(
                    transcript=st.session_state.state.get('transcript', ''),
                    klantuitvraag=st.session_state.state.get('klantuitvraag', ''),
                    feedback=feedback,
                    additional_feedback=additional_feedback,
                    user_first_name=user_first_name
                )
                if success:
                    st.success("Bedankt voor uw feedback!")
                else:
                    st.error("Er is een fout opgetreden bij het verzenden van de feedback. Probeer het later opnieuw.")
