import streamlit as st
import os
from utils.audio_processing import transcribe_audio, process_audio_input
from utils.file_processing import process_uploaded_file
from utils.text_processing import update_gesprekslog
from services.summarization_service import analyze_transcript, generate_email
from ui.components import (
    display_transcript, display_klantuitvraag,
    display_input_method_selector, display_text_input, display_file_uploader,
    display_generate_button, display_progress_bar, display_spinner,
    display_success, display_error, display_warning
)
from ui.pages import render_feedback_form, render_conversation_history, render_suggestions

# Set page config at the very beginning
st.set_page_config(page_title="Klantuitvraagtool", page_icon="🔒", layout="wide")

def load_config():
    return {
        "INPUT_METHODS": ["Voer tekst in of plak tekst", "Upload tekst", "Upload audio", "Neem audio op"],
    }

def initialize_session_state():
    if 'state' not in st.session_state:
        st.session_state.state = {
            'transcript': '',
            'edited_transcript': '',
            'klantuitvraag': '',
            'klantuitvraag_versions': [],
            'current_version_index': -1,
            'input_text': '',
            'gesprekslog': [],
            'product_info': '',
            'selected_products': [],
            'suggestions': [],
            'selected_suggestions': [],
            'email_content': '',
            'input_processed': False,
            'analysis_complete': False,
            'transcription_complete': False,
            'active_step': 1,
        }
    elif 'active_step' not in st.session_state.state:
        st.session_state.state['active_step'] = 1

def main():
    st.title("Klantuitvraagtool v0.0.3")
    st.markdown("---")

    config = load_config()
    initialize_session_state()

    steps = ["Input Data", "Analyze", "Recommendations", "Client Report"]
    
    col1, col2, col3, col4 = st.columns(4)
    for i, step in enumerate(steps, 1):
        with locals()[f"col{i}"]:
            if st.session_state.state['active_step'] == i:
                st.markdown(f"**{i}. {step}**")
            elif st.session_state.state['active_step'] > i:
                st.markdown(f"~~{i}. {step}~~")
            else:
                st.markdown(f"{i}. {step}")

    if st.session_state.state['active_step'] == 1:
        st.subheader("Input Client Data")
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
            if display_generate_button():
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
            st.text_area("Transcript:", value=st.session_state.state['transcript'], height=200, key="transcript_display")
            if st.button("Proceed to Analysis"):
                st.session_state.state['active_step'] = 2

    elif st.session_state.state['active_step'] == 2:
        st.subheader("Analysis Results")
        
        if not st.session_state.state['analysis_complete']:
            with st.spinner("Analyzing transcript..."):
                try:
                    analysis_result = analyze_transcript(st.session_state.state['transcript'])
                    st.session_state.state['suggestions'] = analysis_result
                    st.session_state.state['analysis_complete'] = True
                    display_success("Analysis completed!")
                except Exception as e:
                    display_error(f"An error occurred during analysis: {str(e)}")

        if st.session_state.state['analysis_complete']:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Current Coverage")
                st.write("AVB - €1,500,000")
                st.write("Business Interruption - €350,000")
            
            with col2:
                st.markdown("### Identified Risks")
                st.write("- Online platform vulnerability")
                st.write("- Potential underinsurance")

            if st.button("View Recommendations"):
                st.session_state.state['active_step'] = 3

    elif st.session_state.state['active_step'] == 3:
        st.subheader("Recommendations")
        selected_suggestions = render_suggestions(st.session_state.state['suggestions'])
        st.session_state.state['selected_suggestions'] = selected_suggestions

        if st.button("Generate Client Report"):
            st.session_state.state['active_step'] = 4

    elif st.session_state.state['active_step'] == 4:
        st.subheader("Client Report")
        
        if 'email_content' not in st.session_state.state or not st.session_state.state['email_content']:
            with st.spinner("Generating client report..."):
                try:
                    email_content = generate_email(
                        st.session_state.state['transcript'],
                        st.session_state.state['selected_suggestions']
                    )
                    st.session_state.state['email_content'] = email_content
                    display_success("Client report generated!")
                except Exception as e:
                    display_error(f"An error occurred while generating the report: {str(e)}")

        if st.session_state.state.get('email_content'):
            st.download_button(
                label="Download Report",
                data=st.session_state.state['email_content'],
                file_name="InsuranceReport_Client.txt",
                mime="text/plain"
            )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Schedule Follow-up"):
                st.write("Follow-up scheduled!")
        with col2:
            if st.button("Send to Client"):
                st.write("Report sent to client!")

if __name__ == "__main__":
    main()