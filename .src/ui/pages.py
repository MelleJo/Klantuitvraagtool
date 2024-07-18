import streamlit as st
from ui.components import *
from utils.audio_processing import transcribe_audio, process_audio_input
from utils.file_processing import process_uploaded_file
from services.summarization_service import analyze_transcript, generate_email
from services.email_service import send_feedback_email
import os
import html

def render_input_step(config):
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📝 Input Client Data")
    input_method = display_input_method_selector(config["INPUT_METHODS"])

    if input_method == "Upload tekst":
        uploaded_file = display_file_uploader(['txt', 'docx', 'pdf'])
        if uploaded_file:
            transcript = process_uploaded_file(uploaded_file)
            st.session_state.state['transcript'] = transcript
            st.session_state.state['input_processed'] = True
            st.session_state.state['transcription_complete'] = True

    elif input_method == "Voer tekst in of plak tekst":
        input_text = display_text_input()
        if display_generate_button("Process Text"):
            st.session_state.state['transcript'] = input_text
            st.session_state.state['input_processed'] = True
            st.session_state.state['transcription_complete'] = True

    elif input_method in ["Upload audio", "Neem audio op"]:
        if not st.session_state.state['transcription_complete']:
            audio_file_path = process_audio_input(input_method)
            if audio_file_path:
                with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                    transcript = transcribe_audio(audio_file_path)
                    st.session_state.state['transcript'] = transcript
                    st.session_state.state['input_processed'] = True
                    st.session_state.state['transcription_complete'] = True
                os.unlink(audio_file_path)

    if st.session_state.state['input_processed']:
        st.markdown("### 📄 Generated Transcript")
        st.text_area("", value=st.session_state.state['transcript'], height=200, key="transcript_display")
        if st.button("Proceed to Analysis", key="proceed_to_analysis"):
            st.session_state.state['active_step'] = 2
    st.markdown("</div>", unsafe_allow_html=True)

def render_analysis_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("🔍 Analysis Results")
    
    if not st.session_state.state['analysis_complete']:
        with st.spinner("Analyzing transcript..."):
            try:
                analysis_result = analyze_transcript(st.session_state.state['transcript'])
                st.session_state.state['suggestions'] = analysis_result
                st.session_state.state['analysis_complete'] = True
                display_success("Analysis completed successfully!")
                st.write(f"Debug: Analysis result type: {type(analysis_result)}")
                st.write(f"Debug: Analysis result: {analysis_result}")
            except Exception as e:
                display_error(f"An error occurred during analysis: {str(e)}")
                st.write(f"Debug: Full error: {e}")

    if st.session_state.state['analysis_complete']:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Current Coverage")
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            display_metric("AVB", "€1,500,000")
            display_metric("Business Interruption", "€350,000")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ⚠️ Identified Risks")
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            st.write("• Online platform vulnerability")
            st.write("• Potential underinsurance")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("View Recommendations", key="view_recommendations"):
            st.session_state.state['active_step'] = 3
    st.markdown("</div>", unsafe_allow_html=True)



def render_recommendations_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("💡 Recommendations")
    
    st.write(f"Debug: Session state: {st.session_state.state}")
    
    if 'suggestions' not in st.session_state.state or not st.session_state.state['suggestions']:
        st.warning("No recommendations available. Please complete the analysis step first.")
        st.write(f"Debug: Suggestions in session state: {st.session_state.state.get('suggestions')}")
    else:
        st.write(f"Debug: Suggestions type: {type(st.session_state.state['suggestions'])}")
        st.write(f"Debug: Suggestions content: {st.session_state.state['suggestions']}")
        selected_suggestions = render_suggestions(st.session_state.state['suggestions'])
        st.session_state.state['selected_suggestions'] = selected_suggestions

        if selected_suggestions:
            st.success(f"{len(selected_suggestions)} recommendations selected.")
            if st.button("Generate Client Report", key="generate_client_report"):
                st.session_state.state['active_step'] = 4
        else:
            st.info("Please select at least one recommendation to generate a client report.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_client_report_step():
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    st.subheader("📄 Client Report")
    
    if 'email_content' not in st.session_state.state or not st.session_state.state['email_content']:
        with st.spinner("Generating client report..."):
            try:
                email_content = generate_email(
                    st.session_state.state['transcript'],
                    st.session_state.state['selected_suggestions']
                )
                st.session_state.state['email_content'] = email_content
                display_success("Client report generated successfully!")
            except Exception as e:
                display_error(f"An error occurred while generating the report: {str(e)}")

    if st.session_state.state.get('email_content'):
        st.markdown("### 📥 Download Report")
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
            st.markdown(gesprek["klantuitvraag"], unsafe_allow_html=True)

def render_suggestions(suggestions):
    selected_suggestions = []

    st.write(f"Debug: Inside render_suggestions. Suggestions: {suggestions}")

    if not isinstance(suggestions, list):
        st.warning(f"Unexpected suggestions type: {type(suggestions)}")
        return selected_suggestions

    for i, suggestion in enumerate(suggestions):
        st.write(f"Debug: Processing suggestion {i}: {suggestion}")
        
        if not isinstance(suggestion, dict):
            st.warning(f"Unexpected suggestion type: {type(suggestion)}")
            continue

        title = suggestion.get('title', f'Recommendation {i+1}')
        justification = suggestion.get('justification', 'No justification provided')
        specific_risks = suggestion.get('specific_risks', 'No specific risks identified')

        with st.expander(title):
            st.write(f"**Justification:** {justification}")
            st.write(f"**Specific Risks:** {specific_risks}")
            is_selected = st.checkbox("Select this recommendation", key=f"rec_{i}")
            if is_selected:
                selected_suggestions.append(suggestion)

    st.write(f"Debug: Selected suggestions: {selected_suggestions}")
    return selected_suggestions
