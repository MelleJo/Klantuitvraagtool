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
    prompt = """
    Je bent een expert verzekeringsadviseur. Analyseer het volgende transcript en geef een lijst met aanvullende verzekeringsvoorstellen die complementair zijn aan wat al besproken is.
    Focus op:
    1. Potentiële hiaten in de huidige dekking
    2. Risico's die nog niet zijn afgedekt
    3. Nieuwe of aanvullende verzekeringen die de klant mogelijk nodig heeft
    4. Verbeteringen of uitbreidingen van bestaande polissen

    Geef voor elk voorstel:
    1. Een titel
    2. Een korte beschrijving
    3. Een redenering gebaseerd op het transcript, inclusief waarom dit een waardevolle aanvulling zou zijn

    Transcript:
    {transcript}

    Geef je analyse in het volgende JSON-formaat:
    [
        {{"titel": "Aanvullend Voorstel Titel", "beschrijving": "Korte beschrijving van aanvullende dekking", "redenering": "Uitgebreide redenering waarom dit voorstel complementair en waardevol is"}}
    ]
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0.4)
    
    try:
        prompt_template = ChatPromptTemplate.from_template(prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({"transcript": transcript})
        return json.loads(result.content)
    except Exception as e:
        print(f"Error in analyze_transcript: {str(e)}")
        raise e

def generate_email(transcript: str, selected_suggestions: List[Dict[str, str]]) -> str:
    suggestions_text = "\n".join([f"- {s['titel']}: {s['beschrijving']}" for s in selected_suggestions])
    prompt = f"""
    Je bent een verzekeringsadviseur die een e-mail schrijft aan een klant als onderdeel van je zorgplicht. 
    Het doel is om de huidige situatie van de klant te verifiëren, vooral voor klanten die we minder vaak bezoeken of spreken.
    Schrijf een professionele en vriendelijke e-mail die het volgende bevat:

    1. Een korte introductie waarin je uitlegt waarom je contact opneemt (zorgplicht, periodieke check).
    2. Vragen om de huidige situatie van de klant te verifiëren, gebaseerd op het transcript.
    3. Vragen over mogelijke veranderingen in de situatie van de klant sinds het laatste contact.
    4. Introductie van de geselecteerde verzekeringsvoorstellen als mogelijke aanvullingen of verbeteringen.
    5. Een uitnodiging voor een vervolgafspraak om de situatie en eventuele aanpassingen te bespreken.

    Gebruik de volgende informatie:

    Transcript:
    {transcript}

    Geselecteerde Verzekeringsvoorstellen:
    {suggestions_text}

    Zorg ervoor dat de e-mail de nadruk legt op onze zorgplicht en het belang van het up-to-date houden van de verzekeringssituatie van de klant.
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