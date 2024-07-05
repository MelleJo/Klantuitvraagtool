from openai import OpenAI
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import io

def transcribe_audio_api(audio_file):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        response_format="text"
    )
    return transcription['text']

def analyze_text_api(text):
    prompt = f"Analyze the following transcript and extract relevant insurances, insured amounts, and general questions:\n\n{text}"
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0)
    
    prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = prompt_template | chat_model
    
    return chain.invoke({"text": text}).content

def generate_email_api(transcript, analysis):
    prompt = f"Generate an email content based on the following transcript and analysis:\n\nTranscript:\n{transcript}\n\nAnalysis:\n{analysis}"
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0)
    
    prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = prompt_template | chat_model
    
    return chain.invoke({"text": transcript}).content

def generate_attachment_api(analysis):
    prompt = f"Generate an attachment content based on the following analysis:\n\n{analysis}"
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0)
    
    prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = prompt_template | chat_model
    
    return chain.invoke({"text": analysis}).content
