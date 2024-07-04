from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

def analyze_transcript(transcript):
    # Define the prompt to extract relevant information from the transcript
    prompt = f"Analyze the following transcript and extract relevant insurances, insured amounts, and general questions:\n\n{transcript}"
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0)
    
    prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = prompt_template | chat_model
    
    return chain.invoke({"text": transcript}).content
