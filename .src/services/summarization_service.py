import logging
from typing import List, Dict, Any
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.text_processing import load_prompt
import traceback
import os
import simplejson as json
import logging

logging.basicConfig(level=logging.DEBUG)
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
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0.2)

    try:
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | chat_model
        result = chain.invoke({"TRANSCRIPT": transcript})
        
        logger.debug(f"Raw analysis result: {result.content}")
        
        # Log the full content
        logger.info(f"Full AI response:\n{result.content}")
        
        parsed_result = parse_analysis_result(result.content)
        
        if not isinstance(parsed_result, dict):
            raise ValueError(f"Expected dictionary, got {type(parsed_result)}")
        
        if 'recommendations' not in parsed_result or parsed_result['recommendations'] is None:
            logger.warning("No recommendations found in parsed result")
            parsed_result['recommendations'] = []
        
        logger.info(f"Number of recommendations: {len(parsed_result['recommendations'])}")
        for i, rec in enumerate(parsed_result['recommendations']):
            logger.info(f"Recommendation {i+1}: {rec.get('title', 'No title')}")
        
        st.session_state.state['suggestions'] = parsed_result
        logger.debug("Stored parsed result in session state")
        
        return parsed_result
    except Exception as e:
        logger.error(f"Error in analyze_transcript: {str(e)}", exc_info=True)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"error": str(e)}

def parse_analysis_result(content: str) -> Dict[str, Any]:
    result = {
        'current_coverage': [],
        'coverage_gaps': [],
        'recommendations': [],
        'additional_comments': []
    }
    
    current_section = None
    current_recommendation = None
    
    for line in content.split('\n'):
        line = line.strip()
        logger.debug(f"Processing line: {line}")
        
        # Check for section starts
        if '<bestaande_dekking>' in line:
            current_section = 'current_coverage'
            continue
        elif '<dekkingshiaten>' in line:
            current_section = 'coverage_gaps'
            continue
        elif '<verzekeringsaanbevelingen>' in line:
            current_section = 'recommendations'
            continue
        elif '<aanvullende_opmerkingen>' in line:
            current_section = 'additional_comments'
            continue
        
        # Check for section ends
        if line.startswith('</'):
            if current_recommendation:
                result['recommendations'].append(current_recommendation)
                logger.debug(f"Appending recommendation: {current_recommendation}")
            current_recommendation = None
            current_section = None
            continue
        
        # Process content based on current section
        if current_section and line and not line.startswith('<'):
            if current_section == 'recommendations':
                if line.startswith('Aanbeveling:'):
                    if current_recommendation:
                        result['recommendations'].append(current_recommendation)
                    current_recommendation = {'title': line[12:].strip(), 'description': '', 'rechtvaardiging': '', 'specific_risks': []}
                elif line.startswith('Beschrijving:'):
                    current_recommendation['description'] = line[12:].strip()
                elif line.startswith('Rechtvaardiging:'):
                    current_recommendation['rechtvaardiging'] = line[16:].strip()
                elif line.startswith('Specifieke risico\'s:'):
                    current_recommendation['specific_risks'].append(line[19:].strip())
                elif current_recommendation:
                    current_recommendation['specific_risks'].append(line)
            else:
                result[current_section].append(line)
    
    # Add any remaining recommendation
    if current_recommendation:
        result['recommendations'].append(current_recommendation)
    
    logger.info(f"Parsed result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result




logger = logging.getLogger(__name__)

def generate_email(transcript: str, analysis: Dict[str, Any], selected_recommendations: List[Dict[str, Any]]) -> str:
    current_coverage = analysis.get('current_coverage', [])
    current_coverage_str = "\n".join([f"- {item}" for item in current_coverage]) if current_coverage else "Geen huidige dekking geïdentificeerd."

    company_name = "Uw bedrijf"  # You might want to extract this from the transcript if possible

    prompt = """
    Je bent een verzekeringsadviseur die een e-mail schrijft aan een klant als onderdeel van je zorgplicht.
    Het doel is om de huidige situatie van de klant te verifiëren en gericht advies te geven over mogelijke verbeteringen in hun verzekeringsdekking, met focus op de geselecteerde aanbevelingen.
    Schrijf een professionele en vriendelijke e-mail met de volgende structuur en inhoud:

    Onderwerp: {title}

    1. Korte introductie (2-3 zinnen):
    - Verklaar de reden voor contact (zorgplicht, periodieke check)
    - Noem het doel van de e-mail

    2. Huidige Dekking:
    {current_coverage}

    3. Aanbevelingen:
    Voor elke geselecteerde aanbeveling, schrijf een korte paragraaf (2-3 zinnen) die:
    - Begint met "Aangezien..." en verwijst naar een specifiek aspect van het bedrijf van de klant
    - Een concreet risico beschrijft dat relevant is voor hun situatie, specifiek voor hun branche
    - Uitlegt hoe de aanbevolen verzekering kan helpen dit risico te mitigeren

    4. Aanvullende Aandachtspunten:
    - Geef 3-5 korte, adviserende punten over andere belangrijke zaken die aandacht verdienen
    - Formuleer elk punt als een suggestie of aanbod om te helpen
    - Houd de toon consistent met de rest van de e-mail

    5. Vervolgstappen:
    - Nodig de klant uit voor een vervolgafspraak
    - Geef een korte afsluiting die het belang van de check benadrukt
    - Voeg een zin toe die de klant uitnodigt om op de e-mail te reageren voor het maken van een telefonische afspraak

    Gebruik de volgende informatie:

    Transcript:
    {transcript}

    Geselecteerde aanbevelingen:
    {selected_recommendations}

    Richtlijnen:
    - Personaliseer de e-mail voor de klant en hun bedrijf, gebruik informatie uit het transcript
    - Gebruik 'u' en 'uw bedrijf' in plaats van de bedrijfsnaam te herhalen
    - Leg de nadruk op de zorgplicht en het belang van up-to-date verzekeringsdekking
    - Gebruik Nederlandse verzekeringstermen en -producten
    - Vermijd het gebruik van placeholders; verwijs naar de klant en jezelf op een algemene maar persoonlijke manier
    - Houd de toon professioneel maar toegankelijk
    - Presenteer de aanbevelingen als opties om risico's te mitigeren, niet als essentiële producten
    - Zorg dat elke sectie kort en bondig is
    - Bespreek alleen de geselecteerde aanbevelingen in detail
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0.3)

    try:
        prompt_template = ChatPromptTemplate.from_template(prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({
            "title": f"Periodieke verzekeringscheck en aanbevelingen voor {company_name}",
            "current_coverage": current_coverage_str,
            "transcript": transcript,
            "selected_recommendations": json.dumps(selected_recommendations, ensure_ascii=False, indent=2)
        })
        return result.content
    except Exception as e:
        logger.error(f"Error in generate_email: {str(e)}")
        raise e