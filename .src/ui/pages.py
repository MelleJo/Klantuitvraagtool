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
from services.summarization_service import analyze_transcript, generate_email
from services.email_service import send_feedback_email
import os
import html
import time
from utils.session_state import update_session_state, move_to_step, clear_analysis_results
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def render_input_step(config):
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📝 Gegevens invoeren")
    input_method = st.selectbox("Selecteer invoermethode:", config["INPUT_METHODS"])

    if input_method == "Upload tekstbestand":
        uploaded_file = st.file_uploader("Upload een bestand:", type=['txt', 'docx', 'pdf'])
        if uploaded_file:
            transcript = process_uploaded_file(uploaded_file)
            update_session_state('transcript', transcript)
            update_session_state('input_processed', True)
            update_session_state('transcription_complete', True)

    elif input_method == "Voer tekst in of plak tekst":
        input_text = st.text_area("Voer tekst in of plak tekst:", height=200, key="input_text_area")
        # Update session state immediately when text is entered
        update_session_state('transcript', input_text)
        update_session_state('input_processed', True)
        update_session_state('transcription_complete', True)

    elif input_method == "Upload audiobestand":
        uploaded_file = st.file_uploader("Upload een audiobestand", type=["wav", "mp3", "m4a", "ogg", "weba", "mp4"])
        if uploaded_file:
            audio_file_path = process_audio_input(input_method, uploaded_file)
            if audio_file_path:
                with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                    transcript = transcribe_audio(audio_file_path)
                    update_session_state('transcript', transcript)
                    update_session_state('input_processed', True)
                    update_session_state('transcription_complete', True)
                os.unlink(audio_file_path)

    elif input_method == "Neem audio op":
        audio_file_path = process_audio_input(input_method)
        if audio_file_path:
            with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                transcript = transcribe_audio(audio_file_path)
                update_session_state('transcript', transcript)
                update_session_state('input_processed', True)
                update_session_state('transcription_complete', True)
            os.unlink(audio_file_path)

    if st.session_state.get('input_processed', False):
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
        recommendations = st.session_state.get('suggestions', {}).get('recommendations', [])
        
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
            
            if selected_recommendations:
                if st.button("Genereer klantrapport"):
                    st.session_state.active_step = 4
            else:
                st.info("Selecteer ten minste één aanbeveling om een klantrapport te genereren.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
def render_client_report_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📄 Klantrapport")
    
    if 'email_content' not in st.session_state or not st.session_state.get('email_content'):
        if st.button("Genereer klantrapport"):
            progress_placeholder = st.empty()
            email_placeholder = st.empty()
            
            try:
                with st.spinner("Rapport wordt gegenereerd..."):
                    stages = ["Denken...", "Schrijven...", "Feedback verwerken...", "Verbeterde versie schrijven..."]
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, stage in enumerate(stages):
                        status_text.text(stage)
                        progress_bar.progress((i + 1) / len(stages))
                        
                        if i == 0:
                            transcript = st.session_state.get('transcript', '')
                            suggestions = st.session_state.get('suggestions', {})
                            selected_suggestions = st.session_state.get('selected_suggestions', [])

                            logging.info(f"Transcript: {transcript}")
                            logging.info(f"Suggestions: {suggestions}")
                            logging.info(f"Selected suggestions: {selected_suggestions}")

                            current_coverage = suggestions.get('current_coverage', [])
                            enhanced_coverage = [{"title": item, "coverage": item} for item in current_coverage]

                            logging.info(f"Enhanced coverage: {enhanced_coverage}")

                            try:
                                email_content = generate_email(
                                    transcript=transcript,
                                    enhanced_coverage=enhanced_coverage,
                                    selected_recommendations=selected_suggestions
                                )
                            except Exception as e:
                                logging.error(f"Error in generate_email: {str(e)}")
                                logging.error(f"Error type: {type(e)}")
                                logging.error(f"Error args: {e.args}")
                                raise
                        
                        time.sleep(1)
                    
                    update_session_state('email_content', email_content)
                    progress_bar.empty()
                    status_text.empty()
                    st.success("Klantrapport succesvol gegenereerd!")
            except Exception as e:
                logging.error(f"Error in render_client_report_step: {str(e)}")
                logging.error(f"Error type: {type(e)}")
                logging.error(f"Error args: {e.args}")
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
                    transcript=st.session_state.get('transcript', ''),
                    klantuitvraag=st.session_state.get('klantuitvraag', ''),
                    feedback=feedback,
                    additional_feedback=additional_feedback,
                    user_first_name=user_first_name
                )
                if success:
                    st.success("Bedankt voor uw feedback!")
                else:
                    st.error("Er is een fout opgetreden bij het verzenden van de feedback. Probeer het later opnieuw.")

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