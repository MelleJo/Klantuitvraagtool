from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

def generate_email(transcript, analysis):
    # Define the prompt to generate email content based on the transcript and analysis
    prompt = f"Generate an email content based on the following transcript and analysis:\n\nTranscript:\n{transcript}\n\nAnalysis:\n{analysis}"
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0)
    
    prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = prompt_template | chat_model
    
    return chain.invoke({"text": transcript}).content
