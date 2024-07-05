import streamlit as st
from streamlit_mic_recorder import mic_recorder
from utils.api_calls import transcribe_audio_api

def transcribe_audio(audio_file):
    return transcribe_audio_api(audio_file)

def transcribe_text(text):
    return text

def whisper_stt(start_prompt="Start recording", stop_prompt="Stop recording", just_once=False,
                use_container_width=False, language=None, callback=None, args=(), kwargs=None, key=None):
    audio = mic_recorder(start_prompt=start_prompt, stop_prompt=stop_prompt, just_once=just_once,
                         use_container_width=use_container_width, key=key)
    new_output = False
    if audio is None:
        output = None
    else:
        id = audio['id']
        new_output = (id > st.session_state.get('_last_speech_to_text_transcript_id', 0))
        if new_output:
            st.session_state['_last_speech_to_text_transcript_id'] = id
            audio_bio = io.BytesIO(audio['bytes'])
            audio_bio.name = 'audio.mp3'
            output = transcribe_audio_api(audio_bio, language)
            st.session_state['_last_speech_to_text_transcript'] = output
        elif not just_once:
            output = st.session_state.get('_last_speech_to_text_transcript', None)
        else:
            output = None

    if key:
        st.session_state[key + '_output'] = output
    if new_output and callback:
        callback(*args, **(kwargs or {}))
    return output
