import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.text_processing import load_prompt
from typing import List, Dict
import json

def generate_klantuitvraag(text):
    custom_prompt = load_prompt("klantuitvraag_prompt.txt")
    full_prompt = f"{custom_prompt}\n\nInput tekst: \"{text}\"\n\nGenereer nu een klantuitvraag op basis van deze input:"
    
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4", temperature=0)
    
    try:
        prompt_template = ChatPromptTemplate.from_template(full_prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({}).content
        return result
    except Exception as e:
        print(f"Error in generate_klantuitvraag: {str(e)}")
        raise e

def run_klantuitvraag(text):
    try:
        klantuitvraag = generate_klantuitvraag(text)
        return {"klantuitvraag": klantuitvraag, "error": None}
    except Exception as e:
        return {"klantuitvraag": None, "error": str(e)}

def analyze_transcript(transcript: str) -> List[Dict[str, str]]:
    prompt = f"""
    Je bent een expert verzekeringsadviseur. Analyseer het volgende transcript en geef een lijst met verzekeringsvoorstellen.
    Elk voorstel moet een titel, een korte beschrijving en een redenering bevatten op basis van de inhoud van het transcript.

    Transcript:
    {{transcript}}

    Geef je analyse in het volgende JSON-formaat:
    [
        {{"titel": "Voorstel Titel", "beschrijving": "Korte beschrijving", "redenering": "Redenering gebaseerd op transcript"}}
    ]
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4", temperature=0.7)
    
    try:
        prompt_template = ChatPromptTemplate.from_template(prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({"transcript": transcript}).content
        return json.loads(result)
    except Exception as e:
        print(f"Error in analyze_transcript: {str(e)}")
        raise e

def generate_email(transcript: str, selected_suggestions: List[Dict[str, str]]) -> str:
    suggestions_text = "\n".join([f"- {s['titel']}: {s['beschrijving']}" for s in selected_suggestions])
    prompt = f"""
    Je bent een verzekeringsadviseur die een e-mail schrijft aan een klant op basis van een gespreksverslag en geselecteerde verzekeringsvoorstellen.
    Schrijf een professionele en vriendelijke e-mail die het volgende bevat:
    1. Een samenvatting van het gesprek
    2. De geselecteerde verzekeringsvoorstellen
    3. Een uitnodiging voor een vervolgafspraak

    Transcript:
    {transcript}

    Geselecteerde Voorstellen:
    {suggestions_text}

    Genereer de e-mailinhoud:
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4", temperature=0.7)
    
    try:
        prompt_template = ChatPromptTemplate.from_template(prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({"transcript": transcript, "suggestions": suggestions_text}).content
        return result
    except Exception as e:
        print(f"Error in generate_email: {str(e)}")
        raise e

print("summarization_service.py loaded successfully")