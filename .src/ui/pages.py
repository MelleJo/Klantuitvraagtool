import streamlit as st
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
    st.subheader("📝 Input Client Data")
    input_method = display_input_method_selector(config["INPUT_METHODS"])

    if input_method == "Upload tekst":
        uploaded_file = display_file_uploader(['txt', 'docx', 'pdf'])
        if uploaded_file:
            transcript = process_uploaded_file(uploaded_file)
            update_session_state('transcript', transcript)
            update_session_state('input_processed', True)
            update_session_state('transcription_complete', True)

    elif input_method == "Voer tekst in of plak tekst":
        input_text = display_text_input()
        if display_generate_button("Process Text"):
            update_session_state('transcript', input_text)
            update_session_state('input_processed', True)
            update_session_state('transcription_complete', True)

    elif input_method in ["Upload audio", "Neem audio op"]:
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
        st.markdown("### 📄 Generated Transcript")
        st.text_area("", value=st.session_state.state['transcript'], height=200, key="transcript_display")
    st.markdown("</div>", unsafe_allow_html=True)

def render_analysis_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("🔍 Analysis Results")
    
    if not st.session_state.state['analysis_complete']:
        with st.spinner("Analyzing transcript..."):
            try:
                analysis_result = analyze_transcript(st.session_state.state['transcript'])
                if "error" in analysis_result:
                    raise Exception(analysis_result["error"])
                update_session_state('suggestions', analysis_result)
                update_session_state('analysis_complete', True)
                display_success("Analysis completed successfully!")
            except Exception as e:
                display_error(f"An error occurred during analysis: {str(e)}")
                st.stop()

    if st.session_state.state['analysis_complete']:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Current Coverage")
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            current_coverage = st.session_state.state['suggestions'].get('current_coverage', [])
            if isinstance(current_coverage, list):
                for coverage in current_coverage:
                    if isinstance(coverage, dict) and 'name' in coverage and 'value' in coverage:
                        display_metric(coverage['name'], coverage['value'])
                    else:
                        st.write(coverage)
            else:
                st.write(current_coverage)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ⚠️ Identified Risks")
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            identified_risks = st.session_state.state['suggestions'].get('identified_risks', [])
            if isinstance(identified_risks, list):
                for risk in identified_risks:
                    st.write(f"• {risk}")
            else:
                st.write(identified_risks)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def render_recommendations_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("💡 Recommendations")
    
    if 'suggestions' not in st.session_state.state or not st.session_state.state['suggestions']:
        st.warning("No recommendations available. Please complete the analysis step first.")
    else:
        recommendations = st.session_state.state['suggestions'].get('recommendations', [])
        selected_recommendations = render_enhanced_suggestions(recommendations)
        update_session_state('selected_suggestions', selected_recommendations)

        if selected_recommendations:
            st.success(f"{len(selected_recommendations)} recommendations selected.")
            if st.button("Generate Client Report", key="generate_client_report"):
                st.session_state.state['active_step'] = 4
                st.rerun()
        else:
            st.info("Please select at least one recommendation to generate a client report.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_enhanced_suggestions(recommendations):
    selected_recommendations = []
    try:
        if not isinstance(recommendations, list):
            logger.warning(f"Recommendations is not a list. Type: {type(recommendations)}")
            st.warning("No valid recommendations available.")
            return selected_recommendations

        for i, rec in enumerate(recommendations):
            try:
                if not isinstance(rec, dict):
                    logger.warning(f"Recommendation {i} is not a dictionary. Type: {type(rec)}")
                    continue

                title = rec.get('title', f'Recommendation {i+1}')
                with st.expander(title, expanded=False):
                    st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
                    description = rec.get('description', 'No description provided.')
                    st.markdown(f'<p class="recommendation-title">Description:</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="recommendation-content">{description}</p>', unsafe_allow_html=True)
                    
                    st.markdown('<p class="recommendation-title">Specific Risks:</p>', unsafe_allow_html=True)
                    risks = rec.get('specific_risks', [])
                    if isinstance(risks, list) and risks:
                        st.markdown('<ul class="recommendation-list">', unsafe_allow_html=True)
                        for risk in risks:
                            st.markdown(f'<li>{risk}</li>', unsafe_allow_html=True)
                        st.markdown('</ul>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="recommendation-content">No specific risks provided.</p>', unsafe_allow_html=True)
                    
                    if st.checkbox("Select this recommendation", key=f"rec_{i}"):
                        selected_recommendations.append(rec)
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                logger.error(f"Error rendering recommendation {i}: {str(e)}")
                st.error(f"Error displaying recommendation {i+1}")
        
    except Exception as e:
        logger.error(f"Error in render_enhanced_suggestions: {str(e)}")
        st.error("An error occurred while displaying recommendations.")
    
    return selected_recommendations

def render_client_report_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📄 Client Report")
    
    if 'email_content' not in st.session_state.state or not st.session_state.state['email_content']:
        with st.spinner("Generating client report..."):
            try:
                email_content = generate_email(
                    st.session_state.state['transcript'],
                    st.session_state.state['suggestions']
                )
                update_session_state('email_content', email_content)
                display_success("Client report generated successfully!")
            except Exception as e:
                logger.error(f"Error in render_client_report_step: {str(e)}")
                display_error(f"An error occurred while generating the report: {str(e)}")
                st.stop()

    if st.session_state.state.get('email_content'):
        st.markdown("### 📥 Report Content")
        st.text_area("Generated Report", value=st.session_state.state['email_content'], height=300, key="report_display")
        
        st.download_button(
            label="Download Report",
            data=st.session_state.state['email_content'],
            file_name="InsuranceReport_Client.txt",
            mime="text/plain"
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📅 Schedule Follow-up", key="schedule_followup"):
            st.write("Follow-up scheduled!")
    with col2:
        if st.button("📤 Send to Client", key="send_to_client"):
            st.write("Report sent to client!")
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
            st.markdown("**Gegenereerde E-mail:**")
            st.markdown(f'<div class="content">{gesprek["klantuitvraag"]}</div>', unsafe_allow_html=True)