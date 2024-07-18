import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.text_processing import load_prompt
from typing import Dict, Any, List

def generate_klantuitvraag(text: str) -> str:
    custom_prompt = load_prompt("klantuitvraag_prompt.txt")
    full_prompt = f"{custom_prompt}\n\nInput tekst: \"{text}\"\n\nGenereer nu een klantuitvraag op basis van deze input:"

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0)

    try:
        prompt_template = ChatPromptTemplate.from_template(full_prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({}).content
        return result
    except Exception as e:
        print(f"Error in generate_klantuitvraag: {str(e)}")
        raise e

def run_klantuitvraag(text: str) -> Dict[str, Any]:
    try:
        klantuitvraag = generate_klantuitvraag(text)
        return {"klantuitvraag": klantuitvraag, "error": None}
    except Exception as e:
        return {"klantuitvraag": None, "error": str(e)}

def analyze_transcript(transcript: str) -> List[Dict[str, str]]:
    prompt_template = load_prompt("insurance_advisor_prompt.txt")
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0.4)

    try:
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | chat_model
        result = chain.invoke({"TRANSCRIPT": transcript})
        
        st.write(f"Debug: Raw analysis result: {result.content}")  # Changed from print to st.write
        
        # Parse the result content into a list of dictionaries
        suggestions = parse_suggestions(result.content)
        
        st.write(f"Debug: Parsed suggestions: {suggestions}")  # Changed from print to st.write
        
        return suggestions
    except Exception as e:
        st.error(f"Error in analyze_transcript: {str(e)}")  # Changed from print to st.error
        raise e

def parse_suggestions(content: str) -> List[Dict[str, str]]:
    suggestions = []
    current_suggestion = {}
    current_key = None

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('<aanbeveling>'):
            current_suggestion = {'title': line[13:].strip()}
        elif line.startswith('<rechtvaardiging>'):
            current_key = 'justification'
        elif line.startswith('<bedrijfsspecifieke_risicos>'):
            current_key = 'specific_risks'
        elif line.startswith('</aanbeveling>'):
            suggestions.append(current_suggestion)
            current_suggestion = {}
            current_key = None
        elif current_key:
            if current_key in current_suggestion:
                current_suggestion[current_key] += ' ' + line
            else:
                current_suggestion[current_key] = line

    return suggestions

def generate_email(transcript: str, analysis: str) -> str:
    prompt = f"""
    Je bent een verzekeringsadviseur die een e-mail schrijft aan een klant als onderdeel van je zorgplicht.
    Het doel is om de huidige situatie van de klant te verifiëren en advies te geven over mogelijke verbeteringen in hun verzekeringsdekking.
    Schrijf een professionele en vriendelijke e-mail die het volgende bevat:

    1. Een korte introductie waarin je uitlegt waarom je contact opneemt (zorgplicht, periodieke check).
    2. Een samenvatting van hun huidige dekking, gebaseerd op de analyse.
    3. Een overzicht van de geïdentificeerde dekkingshiaten en waarom deze belangrijk zijn voor de klant.
    4. Je verzekeringsaanbevelingen, met uitleg waarom deze belangrijk zijn voor de specifieke bedrijfssituatie van de klant.
    5. Een uitnodiging voor een vervolgafspraak om de situatie en eventuele aanpassingen te bespreken.

    Gebruik de volgende informatie:

    Transcript:
    {transcript}

    Analyse:
    {analysis}

    Zorg ervoor dat de e-mail de nadruk legt op onze zorgplicht en het belang van het up-to-date houden van de verzekeringssituatie van de klant.
    De e-mail moet in het Nederlands zijn en verwijzen naar Nederlandse verzekeringsproducten.
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0.3)

    try:
        prompt_template = ChatPromptTemplate.from_template(prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({"transcript": transcript, "analysis": analysis}).content
        return result
    except Exception as e:
        print(f"Error in generate_email: {str(e)}")
        raise e

print("summarization_service.py loaded successfully")