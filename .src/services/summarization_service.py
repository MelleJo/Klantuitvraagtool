import json
import logging
from typing import List, Dict, Any
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.text_processing import load_prompt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.error(f"Error in generate_klantuitvraag: {str(e)}")
        raise e

def run_klantuitvraag(text: str) -> Dict[str, Any]:
    try:
        klantuitvraag = generate_klantuitvraag(text)
        return {"klantuitvraag": klantuitvraag, "error": None}
    except Exception as e:
        logger.error(f"Error in run_klantuitvraag: {str(e)}")
        return {"klantuitvraag": None, "error": str(e)}

def analyze_transcript(transcript: str) -> Dict[str, Any]:
    prompt_template = load_prompt("insurance_advisor_prompt.txt")
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0.4)

    try:
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | chat_model
        result = chain.invoke({"TRANSCRIPT": transcript})
        
        logger.info(f"Raw analysis result: {result.content}")
        
        parsed_result = parse_analysis_result(result.content)
        
        logger.info(f"Parsed analysis result: {parsed_result}")
        
        return parsed_result
    except Exception as e:
        logger.error(f"Error in analyze_transcript: {str(e)}")
        raise e

def parse_analysis_result(content: str) -> Dict[str, Any]:
    result = {
        'current_coverage': [],
        'identified_risks': [],
        'recommendations': [],
        'additional_comments': []
    }
    
    # Parse the content and populate the result dictionary
    lines = content.split('\n')
    current_section = None
    current_recommendation = None
    for line in lines:
        line = line.strip()
        if line.startswith('<bestaande_dekking>'):
            current_section = 'current_coverage'
        elif line.startswith('<dekkingshiaten>'):
            current_section = 'identified_risks'
        elif line.startswith('<verzekeringsaanbevelingen>'):
            current_section = 'recommendations'
        elif line.startswith('<aanvullende_opmerkingen>'):
            current_section = 'additional_comments'
        elif line.startswith('</'):
            if current_recommendation:
                result['recommendations'].append(current_recommendation)
                current_recommendation = None
            current_section = None
        elif current_section == 'current_coverage' and ':' in line:
            name, value = line.split(':', 1)
            result['current_coverage'].append({'name': name.strip(), 'value': value.strip()})
        elif current_section == 'identified_risks' and line:
            result['identified_risks'].append(line)
        elif current_section == 'recommendations':
            if line.startswith('<aanbeveling>'):
                if current_recommendation:
                    result['recommendations'].append(current_recommendation)
                current_recommendation = {'title': line[12:].strip()}
            elif line.startswith('<rechtvaardiging>'):
                current_recommendation['justification'] = line[16:].strip()
            elif line.startswith('<bedrijfsspecifieke_risicos>'):
                current_recommendation['specific_risks'] = line[28:].strip()
            elif current_recommendation:
                if 'justification' in current_recommendation:
                    current_recommendation['justification'] += ' ' + line
                elif 'specific_risks' in current_recommendation:
                    current_recommendation['specific_risks'] += ' ' + line
        elif current_section == 'additional_comments' and line:
            result['additional_comments'].append(line)
    
    if current_recommendation:
        result['recommendations'].append(current_recommendation)
    
    return result

def parse_recommendation(lines: List[str]) -> Dict[str, str]:
    recommendation = {}
    current_key = None
    for line in lines:
        line = line.strip()
        if line.startswith('<aanbeveling>'):
            current_key = 'title'
        elif line.startswith('<rechtvaardiging>'):
            current_key = 'justification'
        elif line.startswith('<bedrijfsspecifieke_risicos>'):
            current_key = 'specific_risks'
        elif line.startswith('</aanbeveling>'):
            break
        elif current_key:
            if current_key in recommendation:
                recommendation[current_key] += ' ' + line
            else:
                recommendation[current_key] = line
    return recommendation

def generate_email(transcript: str, analysis: Dict[str, Any]) -> str:
    prompt = """
    Je bent een verzekeringsadviseur die een e-mail schrijft aan een klant als onderdeel van je zorgplicht.
    Het doel is om de huidige situatie van de klant te verifiëren en advies te geven over mogelijke verbeteringen in hun verzekeringsdekking.
    Schrijf een professionele en vriendelijke e-mail die het volgende bevat:

    1. Een korte introductie waarin je uitlegt waarom je contact opneemt (zorgplicht, periodieke check).
    2. Een samenvatting van hun huidige dekking, gebaseerd op de analyse.
    3. Een overzicht van de geïdentificeerde dekkingshiaten en waarom deze belangrijk zijn voor de klant.
    4. Je verzekeringsaanbevelingen, met uitleg waarom deze belangrijk zijn voor de specifieke bedrijfssituatie van de klant.
    5. Een uitnodiging voor een vervolgafspraak om de situatie en eventuele aanpassingen te bespreken.

    Gebruik de volgende informatie:

    Transcript: {transcript}

    Analyse: {analysis}

    Zorg ervoor dat de e-mail de nadruk legt op onze zorgplicht en het belang van het up-to-date houden van de verzekeringssituatie van de klant.
    De e-mail moet in het Nederlands zijn en verwijzen naar Nederlandse verzekeringsproducten.
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0.3)

    try:
        prompt_template = ChatPromptTemplate.from_template(prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({
            "transcript": transcript,
            "analysis": json.dumps(analysis, ensure_ascii=False)
        })
        return result.content
    except Exception as e:
        logger.error(f"Error in generate_email: {str(e)}")
        raise e

logger.info("summarization_service.py loaded successfully")