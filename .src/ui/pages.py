# pages.py
import os
import time
import math
import html
import logging
from typing import List, Dict, Any
from ui.checklist import recording_checklist

import streamlit as st
import json
from openai import OpenAI

from services.summarization_service import load_product_descriptions, analyze_transcript
from services.email_generation import generate_email_wrapper
from services.email_service import send_feedback_email
from utils.text_processing import load_guidelines
from utils.audio_processing import transcribe_audio, process_audio_input
from utils.file_processing import process_uploaded_file
from utils.session_state import update_session_state, move_to_step, clear_analysis_results

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

from autogen_agents import correction_AI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_available_insurances(analysis_result: Dict[str, Any]) -> List[str]:
    try:
        # Get the absolute path to the current file
        current_file_path = os.path.abspath(__file__)
        
        # Navigate to the project root (assuming 'pages.py' is in 'src/ui/')
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        
        # Construct the path to the insurance_guidelines directory
        guidelines_dir = os.path.join(project_root, '.src', 'insurance_guidelines')
        
        if not os.path.exists(guidelines_dir):
            st.error(f"The directory {guidelines_dir} does not exist.")
            raise FileNotFoundError(f"The directory {guidelines_dir} does not exist.")
        
        available_files = [f.split('.')[0] for f in os.listdir(guidelines_dir) if f.endswith('.txt')]
        
        # Prepare the analysis content
        analysis_content = json.dumps(analysis_result, ensure_ascii=False)
        
        # Use GPT-4o-mini to identify relevant insurances
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that identifies relevant insurance types from an analysis."},
                {"role": "user", "content": f"Given the following analysis result, identify the relevant insurance types from this list: {', '.join(available_files)}. Respond with only the relevant insurance types, separated by commas.\n\nAnalysis:\n{analysis_content}"}
            ],
            temperature=0.2
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
        col1, col2 = st.columns([3, 2])
        with col1:
            audio_file_path = process_audio_input(input_method)
            if audio_file_path:
                with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                    transcript = transcribe_audio(audio_file_path)
                    update_session_state('transcript', transcript)
                    update_session_state('input_processed', True)
                    update_session_state('transcription_complete', True)
                st.success("Audio succesvol opgenomen en getranscribeerd!")
        with col2:
            recording_checklist()

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
                transcript = st.session_state.get('transcript', '')
                if not transcript:
                    st.error("Geen transcript gevonden om te analyseren.")
                    return
                
                analysis_result = analyze_transcript(transcript)
                if "error" in analysis_result:
                    raise Exception(analysis_result["error"])
                
                # Initialize recommendations list
                recommendations = []
                
                # Add advisor questions to recommendations
                for q in analysis_result.get('advisor_questions', []):
                    recommendations.append({
                        "title": q,
                        "description": q,
                        "type": "advisor",
                        "selected": False
                    })
                
                # Add AI risks to recommendations
                for r in analysis_result.get('ai_risks', []):
                    recommendations.append({
                        "title": r,
                        "description": r,
                        "type": "ai",
                        "selected": False
                    })
                
                # Update session state
                update_session_state('suggestions', analysis_result)
                update_session_state('recommendations', recommendations)
                update_session_state('analysis_complete', True)
                
                st.success("Analyse succesvol afgerond!")
            except Exception as e:
                st.error(f"Er is een fout opgetreden tijdens de analyse: {str(e)}")
                logger.error(f"Analysis error: {str(e)}")
                return

    if st.session_state.get('analysis_complete', False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 100%;'>
                <h3 style='color: #1E40AF;'>📊 Huidige dekking</h3>
                <ul style='list-style-type: none; padding-left: 0;'>
            """, unsafe_allow_html=True)
            
            current_coverage = st.session_state.get('suggestions', {}).get('current_coverage', [])
            for coverage in current_coverage:
                st.markdown(f"<li>• {coverage}</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style='background-color: #e6f0ff; padding: 20px; border-radius: 10px; height: 100%;'>
                <h3 style='color: #1E40AF;'>❓ Vragen/opmerkingen adviseur</h3>
                <ul style='list-style-type: none; padding-left: 0;'>
            """, unsafe_allow_html=True)
            
            advisor_questions = st.session_state.get('suggestions', {}).get('advisor_questions', [])
            for question in advisor_questions:
                st.markdown(f"<li>• {question}</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style='background-color: #fff0f0; padding: 20px; border-radius: 10px; height: 100%;'>
                <h3 style='color: #1E40AF;'>⚠️ AI aanvullende risico's</h3>
                <ul style='list-style-type: none; padding-left: 0;'>
            """, unsafe_allow_html=True)
            
            ai_risks = st.session_state.get('suggestions', {}).get('ai_risks', [])
            for risk in ai_risks:
                st.markdown(f"<li>• {risk}</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def render_recommendations_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("💡 Aanbevelingen")

    # Check if analysis is complete and recommendations exist
    if not st.session_state.get('analysis_complete', False):
        st.warning("Voer eerst de analysestap uit voordat u aanbevelingen kunt bekijken.")
        return

    recommendations = st.session_state.get('recommendations', [])
    if not recommendations:
        st.warning("Er zijn geen aanbevelingen beschikbaar. Ga terug naar de analysestap.")
        return

    st.write("Selecteer de aanbevelingen die u wilt opnemen in het rapport:")

    # Add "Select All" button
    if st.button("Selecteer Alles"):
        for rec in recommendations:
            rec['selected'] = True
        update_session_state('recommendations', recommendations)
        st.rerun()

    # Create checkboxes for each recommendation
    updated_recommendations = []
    for i, rec in enumerate(recommendations):
        is_selected = st.checkbox(
            rec['title'],
            key=f"rec_checkbox_{i}",
            value=rec.get('selected', False)
        )
        rec['selected'] = is_selected
        updated_recommendations.append(rec)

    # Update session state with the updated recommendations
    update_session_state('recommendations', updated_recommendations)

    # Filter selected recommendations
    selected_recommendations = [rec for rec in updated_recommendations if rec['selected']]
    update_session_state('selected_suggestions', selected_recommendations)

    if selected_recommendations:
        st.success(f"{len(selected_recommendations)} aanbevelingen geselecteerd.")
        if st.button("Genereer e-mail"):
            move_to_step(4)
            st.rerun()
    else:
        st.info("Selecteer ten minste één aanbeveling om een klantrapport te genereren.")

    st.markdown("</div>", unsafe_allow_html=True)

def render_client_report_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📄 Klantrapport")

    # Load guidelines and product descriptions
    guidelines = load_guidelines()
    product_descriptions = load_product_descriptions()

    # Initialize identified_insurances
    identified_insurances = st.session_state.get('identified_insurances', [])

    if 'corrected_email_content' not in st.session_state:
        if st.button("Genereer e-mail"):
            with st.spinner("Rapport wordt gegenereerd..."):
                try:
                    transcript = st.session_state.get('transcript', '')
                    suggestions = st.session_state.get('suggestions', {})
                    selected_suggestions = st.session_state.get('selected_suggestions', [])
                    
                    # Filter identified insurances based on selected suggestions
                    all_insurances = get_available_insurances(suggestions)
                    selected_titles = [suggestion['title'] for suggestion in selected_suggestions]
                    identified_insurances = [
                        insurance for insurance in all_insurances 
                        if any(title.lower() in insurance.lower() for title in selected_titles)
                    ]

                    current_coverage = suggestions.get('current_coverage', [])
                    enhanced_coverage = [{"title": item, "coverage": item} for item in current_coverage]

                    email_content = generate_email_wrapper(
                        transcript=transcript,
                        enhanced_coverage=enhanced_coverage,
                        selected_recommendations=selected_suggestions,
                        identified_insurances=identified_insurances,
                        guidelines=guidelines,
                        product_descriptions=product_descriptions
                    )

                    st.session_state['corrected_email_content'] = email_content['corrected_email']
                    st.session_state['identified_insurances'] = identified_insurances

                    st.success("Klantrapport succesvol gegenereerd en gecorrigeerd!")
                    st.rerun()

                except Exception as e:
                    logger.error(f"Error in render_client_report_step: {str(e)}")
                    st.error(f"Er is een fout opgetreden bij het genereren van het rapport: {str(e)}")
                    st.stop()

    if st.session_state.get('corrected_email_content'):
        st.markdown("### 📝 Gecorrigeerde rapportinhoud")
        st.markdown(st.session_state.get('corrected_email_content', ''), unsafe_allow_html=True)

        st.download_button(
            label="Download gecorrigeerd rapport",
            data=st.session_state.get('corrected_email_content', ''),
            file_name="Gecorrigeerd_VerzekeringRapport_Klant.md",
            mime="text/markdown"
        )

    # Add debug info in an expander (optional)
    with st.expander("Debug Info", expanded=False):
        st.markdown("### 🐛 Debug Informatie")
        st.json({
            "transcript": st.session_state.get('transcript', '')[:100] + "...",  # Truncated for brevity
            "suggestions": st.session_state.get('suggestions', {}),
            "selected_suggestions": st.session_state.get('selected_suggestions', []),
            "identified_insurances": identified_insurances,
            "corrected_email_content": st.session_state.get('corrected_email_content', '')[:100] + "..."  # Truncated for brevity
        })

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
    """
    Renders the feedback form and handles feedback submission.
    """
    try:
        with st.expander("💬 Feedback", expanded=False):
            with st.form(key="feedback_form", clear_on_submit=True):
                # Form inputs
                user_first_name = st.text_input(
                    "Uw voornaam",
                    key="feedback_name_input",
                    help="Vereist voor het verwerken van uw feedback"
                )
                
                feedback_type = st.radio(
                    "Was deze klantuitvraag nuttig?",
                    options=["Positief", "Negatief"],
                    key="feedback_type_input",
                    horizontal=True
                )
                
                additional_feedback = st.text_area(
                    "Aanvullende feedback",
                    key="feedback_additional_input",
                    help="Optioneel: Deel uw specifieke opmerkingen of suggesties"
                )
                
                # Submit button
                submit_button = st.form_submit_button(
                    label="Verzend feedback",
                    use_container_width=True
                )
                
                if submit_button:
                    if not user_first_name:
                        st.error("⚠️ Voornaam is verplicht bij het geven van feedback.")
                    else:
                        try:
                            # Get current values from session state
                            current_transcript = st.session_state.get('transcript', '')
                            current_email = st.session_state.get('email_content', '')
                            
                            success = send_feedback_email(
                                transcript=current_transcript,
                                klantuitvraag=current_email,
                                feedback=feedback_type,
                                additional_feedback=additional_feedback,
                                user_first_name=user_first_name
                            )
                            
                            if success:
                                st.success("✅ Bedankt voor uw feedback! We waarderen uw input.")
                                st.balloons()
                                # Update session state to indicate feedback was submitted
                                update_session_state('feedback_submitted', True)
                            else:
                                st.error("❌ Er is een fout opgetreden bij het verzenden van de feedback. Probeer het later opnieuw.")
                        
                        except Exception as e:
                            logger.error(f"Error in feedback submission: {str(e)}")
                            st.error(f"❌ Er is een onverwachte fout opgetreden: {str(e)}")
                            
    except Exception as e:
        logger.error(f"Error rendering feedback form: {str(e)}")
        st.error("Er is een fout opgetreden bij het laden van het feedbackformulier.")
