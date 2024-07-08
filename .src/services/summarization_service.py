import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.text_processing import load_prompt, get_local_time


def generate_klantuitvraag(text):
    custom_prompt = load_prompt("klantuitvraag_prompt.txt")
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4", temperature=0)
    
    try:
        prompt_template = ChatPromptTemplate.from_template(custom_prompt)
        chain = prompt_template | chat_model
        return chain.invoke({"text": text}).content
    except Exception as e:
        if "maximum context length" in str(e):
            chunk_size = 100000  # Adjust as needed
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            partial_results = []
            
            for chunk in chunks:
                prompt_template = ChatPromptTemplate.from_template(custom_prompt)
                chain = prompt_template | chat_model
                partial_results.append(chain.invoke({"text": chunk}).content)
            
            final_prompt = "Combineer al deze deelresultaten in één klantuitvraag:\n\n" + "\n\n".join(partial_results)
            final_chain = ChatPromptTemplate.from_template(final_prompt) | chat_model
            return final_chain.invoke({"text": ""}).content
        else:
            raise e

def run_klantuitvraag(text):
    try:
        klantuitvraag = generate_klantuitvraag(text)
        return {"klantuitvraag": klantuitvraag, "error": None}
    except Exception as e:
        return {"klantuitvraag": None, "error": str(e)}
