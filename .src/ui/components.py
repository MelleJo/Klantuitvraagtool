import streamlit as st

def display_transcript(transcript):
    st.subheader("Transcript")
    st.text_area("Gegenereerd Transcript:", value=transcript, height=200, key="generated_transcript", disabled=True)

def display_klantuitvraag(klantuitvraag):
    st.subheader("Gegenereerde E-mail")
    st.text_area("E-mail inhoud:", value=klantuitvraag, height=300)

def display_input_method_selector(input_methods):
    return st.selectbox("Selecteer invoermethode:", input_methods)

def display_text_input():
    return st.text_area("Voer tekst in of plak tekst:", height=200)

def display_file_uploader(allowed_types):
    return st.file_uploader("Upload een bestand:", type=allowed_types)

def display_generate_button():
    return st.button("Genereer")

def display_progress_bar(progress):
    st.progress(progress)

def display_spinner(text):
    return st.spinner(text)

def display_success(message):
    st.success(message)

def display_error(message):
    st.error(message)

def display_warning(message):
    st.warning(message)

def display_audio_recorder():
    return st.audio_recorder(start_text="Start opname", stop_text="Stop opname")

def display_audio_player(audio_bytes):
    st.audio(audio_bytes, format="audio/wav")

def display_checkbox(label, key):
    return st.checkbox(label, key=key)

def display_multiselect(label, options, default=None):
    return st.multiselect(label, options, default=default)

def display_slider(label, min_value, max_value, value, step=1):
    return st.slider(label, min_value, max_value, value, step)

def display_expander(label, content):
    with st.expander(label):
        st.write(content)

def display_tabs(tab_labels):
    return st.tabs(tab_labels)

def display_metric(label, value, delta=None):
    return st.metric(label, value, delta)

def display_download_button(label, data, file_name, mime):
    return st.download_button(label=label, data=data, file_name=file_name, mime=mime)

def display_date_input(label, value=None):
    return st.date_input(label, value)

def display_time_input(label, value=None):
    return st.time_input(label, value)

def display_color_picker(label, value=None):
    return st.color_picker(label, value)

def display_json(data):
    st.json(data)

def display_dataframe(data):
    st.dataframe(data)

def display_line_chart(data):
    st.line_chart(data)

def display_bar_chart(data):
    st.bar_chart(data)

def display_map(data):
    st.map(data)

def display_image(image):
    st.image(image)

def display_video(video):
    st.video(video)

def display_plotly_chart(fig):
    st.plotly_chart(fig)

def display_form(key):
    return st.form(key=key)