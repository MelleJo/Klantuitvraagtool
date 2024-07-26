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
from utils.session_state import update_session_state
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def render_input_step(config):
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📝 Gegevens invoeren")
    input_method = display_input_method_selector(config["INPUT_METHODS"])

    if input_method == "Upload tekstbestand":
        uploaded_file = display_file_uploader(['txt', 'docx', 'pdf'])
        if uploaded_file:
            transcript = process_uploaded_file(uploaded_file)
            update_session_state('transcript', transcript)
            update_session_state('input_processed', True)
            update_session_state('transcription_complete', True)

    elif input_method == "Voer tekst in of plak tekst":
        input_text = display_text_input()
        if display_generate_button("Verwerk tekst"):
            update_session_state('transcript', input_text)
            update_session_state('input_processed', True)
            update_session_state('transcription_complete', True)

    elif input_method in ["Upload audiobestand", "Neem audio op"]:
        if not st.session_state.state['transcription_complete']:
            audio_file_path = process_audio_input(input_method)
            if audio_file_path:
                with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                    transcript = transcribe_audio(audio_file_path)
                    update_session_state('transcript', transcript)
                    update_session_state('input_processed', True)
                    update_session_state('transcription_complete', True)
                os.unlink(audio_file_path)

    if st.session_state.state['input_processed']:
        st.markdown("### 📄 Gegenereerd transcript")
        st.text_area("", value=st.session_state.state['transcript'], height=200, key="transcript_display")
    st.markdown("</div>", unsafe_allow_html=True)

def render_analysis_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("🔍 Analyseresultaten")
    
    if not st.session_state.state['analysis_complete']:
        with st.spinner("Transcript wordt geanalyseerd..."):
            try:
                analysis_result = analyze_transcript(st.session_state.state['transcript'])
                if "error" in analysis_result:
                    raise Exception(analysis_result["error"])
                st.session_state.state['suggestions'] = analysis_result
                st.session_state.state['analysis_complete'] = True
                display_success("Analyse succesvol afgerond!")
            except Exception as e:
                logging.error(f"Er is een fout opgetreden tijdens de analyse: {str(e)}")
                display_error(f"Er is een fout opgetreden tijdens de analyse: {str(e)}")
                st.stop()

    if st.session_state.state['analysis_complete']:
        logger.info(f"Analysis results in session state: {json.dumps(st.session_state.state['suggestions'], indent=2, ensure_ascii=False)}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Huidige dekking")
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            current_coverage = st.session_state.state['suggestions'].get('current_coverage', [])
            if current_coverage:
                for coverage in current_coverage:
                    st.write(f"• {coverage}")
            else:
                st.write("Geen huidige dekking geïdentificeerd.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ⚠️ Geïdentificeerde risico's")
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            identified_risks = st.session_state.state['suggestions'].get('coverage_gaps', [])
            if identified_risks:
                for risk in identified_risks:
                    st.write(f"• {risk}")
            else:
                st.write("Geen specifieke risico's geïdentificeerd.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def render_recommendations_step():
    logging.info("Render_recommendations_step wordt gestart")
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("💡 Aanbevelingen")
    
    if 'suggestions' not in st.session_state.state or not st.session_state.state['suggestions']:
        logging.warning("Geen suggesties in sessietoestand")
        st.warning("Geen aanbevelingen beschikbaar. Voer eerst de analysestap uit.")
    else:
        recommendations = st.session_state.state['suggestions'].get('recommendations', [])
        logging.info(f"Aantal aanbevelingen: {len(recommendations)}")
        
        if not recommendations:
            logging.warning("Er zijn geen aanbevelingen gegenereerd")
            st.warning("Er zijn geen aanbevelingen gegenereerd in de analysestap.")
        else:
            st.write("Selecteer de aanbevelingen die u wilt opnemen in het klantrapport:")
            
            selected_recommendations = []
            for i, rec in enumerate(recommendations):
                title = rec.get('title', f"Aanbeveling {i+1}")
                if st.checkbox(title, key=f"rec_checkbox_{i}"):
                    selected_recommendations.append(rec)
                
                with st.expander(f"Details voor {title}", expanded=False):
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
                if st.button("Genereer klantrapport", key="generate_client_report"):
                    st.session_state.state['active_step'] = 4
                    st.rerun()
            else:
                st.info("Selecteer ten minste één aanbeveling om een klantrapport te genereren.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    logging.info("Render_recommendations_step is voltooid")

def render_client_report_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📄 Klantrapport")
    
    if 'email_content' not in st.session_state.state or not st.session_state.state['email_content']:
        if st.button("Genereer rapport", key="generate_report_button"):
            with st.spinner("Klantrapport wordt gegenereerd..."):
                try:
                    email_content = generate_email(
                        st.session_state.state['transcript'],
                        st.session_state.state['suggestions'],
                        st.session_state.state['selected_suggestions']
                    )
                    update_session_state('email_content', email_content)
                    display_success("Klantrapport succesvol gegenereerd!")
                except Exception as e:
                    logger.error(f"Fout in render_client_report_step: {str(e)}")
                    display_error(f"Er is een fout opgetreden bij het genereren van het rapport: {str(e)}")
                    st.stop()

    if st.session_state.state.get('email_content'):
        st.markdown("### 📥 Rapportinhoud")
        st.text_area("Gegenereerd rapport", value=st.session_state.state['email_content'], height=300, key="report_display")
        
        st.download_button(
            label="Download rapport",
            data=st.session_state.state['email_content'],
            file_name="VerzekeringRapport_Klant.txt",
            mime="text/plain"
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📅 Plan vervolgafspraak", key="schedule_followup"):
            st.write("Vervolgafspraak gepland!")
    with col2:
        if st.button("📤 Verstuur naar klant", key="send_to_client"):
            st.write("Rapport verzonden naar klant!")
    st.markdown("</div>", unsafe_allow_html=True)

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

def render_conversation_history():
    st.subheader("Laatste vijf gesprekken")
    for i, gesprek in enumerate(st.session_state.state.get('gesprekslog', [])):
        with st.expander(f"Gesprek {i+1} op {gesprek['time']}"):
            st.markdown("**Transcript:**")
            st.markdown(f'<div class="content">{html.escape(gesprek["transcript"])}</div>', unsafe_allow_html=True)
            st.markdown("**Gegenereerde e-mail:**")
            st.markdown(f'<div class="content">{gesprek["klantuitvraag"]}</div>', unsafe_allow_html=True)