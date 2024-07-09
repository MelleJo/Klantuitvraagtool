import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.text_processing import load_prompt, get_local_time

def generate_klantuitvraag(text):
    print(f"Debug: generate_klantuitvraag received input: {text[:100]}...")  # Print first 100 chars
    custom_prompt = load_prompt("klantuitvraag_prompt.txt")
    print(f"Debug: Loaded custom prompt: {custom_prompt[:100]}...")  # Print first 100 chars of prompt
    
    # Combine the custom prompt with the input text
    full_prompt = f"{custom_prompt}\n\nInput tekst: \"{text}\"\n\nGenereer nu een klantuitvraag op basis van deze input:"
    
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4", temperature=0)
    
    try:
        prompt_template = ChatPromptTemplate.from_template(full_prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({}).content
        print(f"Debug: Generated klantuitvraag: {result[:100]}...")  # Print first 100 chars of result
        return result
    except Exception as e:
        print(f"Error in generate_klantuitvraag: {str(e)}")
        raise e

def run_klantuitvraag(text):
    print(f"Entering run_klantuitvraag with input: {text[:100]}...")  # Print first 100 chars of input
    try:
        klantuitvraag = generate_klantuitvraag(text)
        print(f"Klantuitvraag generated successfully: {klantuitvraag[:100]}...")  # Print first 100 chars of klantuitvraag
        return {"klantuitvraag": klantuitvraag, "error": None}
    except Exception as e:
        print(f"Error in run_klantuitvraag: {str(e)}")
        return {"klantuitvraag": None, "error": str(e)}

# Make sure run_klantuitvraag is available for import
__all__ = ['run_klantuitvraag']

print("summarization_service.py loaded successfully")