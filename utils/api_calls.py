from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import streamlit as st

def get_openai_client():
    if 'openai_client' not in st.session_state:
        st.session_state.openai_client = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0,
            api_key=st.secrets["OPENAI_API_KEY"]
        )
    return st.session_state.openai_client






##

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
