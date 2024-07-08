import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.text_processing import load_prompt, get_local_time
import sys
import os

print("Starting to load summarization_service.py")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Content of current directory: {os.listdir('.')}")
print(f"sys.path: {sys.path}")

def generate_klantuitvraag(text):
    print(f"Entering generate_klantuitvraag function with text: {text[:100]}...")  # Print first 100 chars of input
    try:
        print("Loading custom prompt")
        custom_prompt = load_prompt("klantuitvraag_prompt.txt")
        print(f"Custom prompt loaded: {custom_prompt[:100]}...")  # Print first 100 chars of prompt
        
        print("Initializing ChatOpenAI")
        chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4", temperature=0)
        print("ChatOpenAI initialized")
        
        print("Creating ChatPromptTemplate")
        prompt_template = ChatPromptTemplate.from_template(custom_prompt)
        print("ChatPromptTemplate created")
        
        print("Creating chain")
        chain = prompt_template | chat_model
        print("Chain created")
        
        print("Invoking chain")
        result = chain.invoke({"text": text})
        print(f"Chain invoked, result: {result.content[:100]}...")  # Print first 100 chars of result
        
        return result.content
    except Exception as e:
        print(f"Error in generate_klantuitvraag: {str(e)}")
        import traceback
        print("Traceback:")
        traceback.print_exc()
        raise

def run_klantuitvraag(text):
    print(f"Entering run_klantuitvraag function with text: {text[:100]}...")  # Print first 100 chars of input
    try:
        print("Calling generate_klantuitvraag")
        klantuitvraag = generate_klantuitvraag(text)
        print(f"generate_klantuitvraag returned: {klantuitvraag[:100]}...")  # Print first 100 chars of result
        return {"klantuitvraag": klantuitvraag, "error": None}
    except Exception as e:
        print(f"Error in run_klantuitvraag: {str(e)}")
        import traceback
        print("Traceback:")
        traceback.print_exc()
        return {"klantuitvraag": None, "error": str(e)}

print("Finished loading summarization_service.py")
print(f"Defined functions: {[name for name in globals() if callable(globals()[name])]}")