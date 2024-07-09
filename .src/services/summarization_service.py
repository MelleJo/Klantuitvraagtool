import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.text_processing import load_prompt, get_local_time

def generate_klantuitvraag(text):
    print(f"Debug: generate_klantuitvraag received input: {text[:100]}...")  # Print first 100 chars
    
    print(f"Entering generate_klantuitvraag with input: {text[:100]}...")  # Print first 100 chars of input
    custom_prompt = load_prompt("klantuitvraag_prompt.txt")
    print(f"Loaded custom prompt: {custom_prompt[:100]}...")  # Print first 100 chars of prompt
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4", temperature=0)
    
    try:
        prompt_template = ChatPromptTemplate.from_template(custom_prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({"text": text}).content
        print(f"Generated klantuitvraag: {result[:100]}...")  # Print first 100 chars of result
        return result
    except Exception as e:
        print(f"Exception in generate_klantuitvraag: {str(e)}")
        if "maximum context length" in str(e):
            print("Handling maximum context length error")
            chunk_size = 100000  # Adjust as needed
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            partial_results = []
            
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                prompt_template = ChatPromptTemplate.from_template(custom_prompt)
                chain = prompt_template | chat_model
                chunk_result = chain.invoke({"text": chunk}).content
                partial_results.append(chunk_result)
                print(f"Chunk {i+1} result: {chunk_result[:100]}...")  # Print first 100 chars of chunk result
            
            final_prompt = "Combineer al deze deelresultaten in één klantuitvraag:\n\n" + "\n\n".join(partial_results)
            final_chain = ChatPromptTemplate.from_template(final_prompt) | chat_model
            final_result = final_chain.invoke({"text": ""}).content
            print(f"Final combined result: {final_result[:100]}...")  # Print first 100 chars of final result
            return final_result
        else:
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