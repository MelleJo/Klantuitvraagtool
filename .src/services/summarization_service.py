import logging
from typing import List, Dict, Any
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks import StreamlitCallbackHandler
from utils.text_processing import load_prompt
import traceback
import simplejson as json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_product_descriptions():
    with open('product_descriptions.json', 'r') as file:
        return json.load(file)

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
        
        parsed_result = parse_analysis_result(result.content)
        
        if not isinstance(parsed_result, dict):
            raise ValueError(f"Expected dictionary, got {type(parsed_result)}")
        
        if 'recommendations' not in parsed_result or parsed_result['recommendations'] is None:
            logger.warning("No recommendations found in parsed result")
            parsed_result['recommendations'] = []
        
        logger.info(f"Number of recommendations: {len(parsed_result['recommendations'])}")
        for i, rec in enumerate(parsed_result['recommendations']):
            logger.info(f"Recommendation {i+1}: {rec.get('title', 'No title')}")
        
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
        
        if line.startswith('<bestaande_dekking>'):
            current_section = 'current_coverage'
        elif line.startswith('<dekkingshiaten>'):
            current_section = 'coverage_gaps'
        elif line.startswith('<verzekeringsaanbevelingen>'):
            current_section = 'recommendations'
        elif line.startswith('<aanvullende_opmerkingen>'):
            current_section = 'additional_comments'
        elif line.startswith('</'):
            if current_recommendation:
                result['recommendations'].append(current_recommendation)
                logger.debug(f"Appending recommendation: {current_recommendation}")
                current_recommendation = None
            if line.startswith('</verzekeringsaanbevelingen>'):
                current_section = None
        elif current_section == 'recommendations':
            if line.startswith('Aanbeveling:'):
                if current_recommendation:
                    result['recommendations'].append(current_recommendation)
                    logger.debug(f"Appending recommendation: {current_recommendation}")
                current_recommendation = {'title': line[12:].strip(), 'description': '', 'rechtvaardiging': '', 'specific_risks': []}
            elif line.startswith('Beschrijving:'):
                current_recommendation['description'] = line[12:].strip()
            elif line.startswith('Rechtvaardiging:'):
                current_recommendation['rechtvaardiging'] = line[16:].strip()
            elif line.startswith('Specifieke risico\'s:'):
                continue  # Skip this line, we'll collect risks in the else clause
            elif current_recommendation:
                if not current_recommendation['specific_risks'] or current_recommendation['specific_risks'][-1].startswith('-'):
                    current_recommendation['specific_risks'].append(line)
                else:
                    current_recommendation['specific_risks'][-1] += ' ' + line
        elif current_section and line and not line.startswith('<'):
            result[current_section].append(line)
    
    # Add any remaining recommendation
    if current_recommendation:
        result['recommendations'].append(current_recommendation)
    
    logger.info(f"Parsed result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result


def load_product_descriptions():
    with open('product_descriptions.json', 'r') as file:
        return json.load(file)

import json
import os
from typing import Dict, Any, List
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

logger = logging.getLogger(__name__)

def load_product_descriptions():
    try:
        with open('product_descriptions.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.warning("product_descriptions.json not found. Using empty dict.")
        return {}
    except json.JSONDecodeError:
        logger.warning("Error decoding product_descriptions.json. Using empty dict.")
        return {}

def generate_email(transcript: str, analysis: Dict[str, Any], selected_recommendations: List[Dict[str, Any]]) -> str:
    current_coverage = analysis.get('current_coverage', [])
    current_coverage_str = "\n".join([f"- {item}" for item in current_coverage]) if current_coverage else "Geen huidige dekking geïdentificeerd."

    product_descriptions = load_product_descriptions()

    prompt = """
    # Verzekeringsadvies E-mail Prompt

    Je bent een expert e-mailschrijver en verzekeringsadviseur. Je taak is het schrijven van een e-mail aan een klant met twee hoofddoelen:
    1. Voldoen aan de zorgplicht
    2. De klant aanzetten tot het bespreken van risico's en het overwegen van aanvullende verzekeringen

    ## Algemene richtlijnen
    - Leg de nadruk op de zorgplicht, zonder deze expliciet te benoemen
    - Vermijd een overduidelijk commerciële toon
    - Bepaal het gebruik van 'u' of 'je' op basis van de branche van de klant:
      - 'Je' voor aannemers, hoveniers, detailhandel, etc.
      - 'U' voor notarissen, advocaten, etc.
    - Gebruik rijke tekstopmaak (bold, italics) waar gepast

    ## E-mailstructuur

    ### 1. Introductie
    - Stel jezelf voor als [relatiebeheerder]
    - Verwijs naar de bestaande verzekeringen van de klant
    - Geef aan dat je je hebt verdiept in het bedrijf en de lopende verzekeringen
    - Noem dat je enkele opvallende zaken hebt geconstateerd die je graag wilt bespreken

    ### 2. Per verzekeringsonderwerp
    Maak voor elk relevant verzekeringsonderwerp een sectie met de volgende structuur:

    #### [Naam verzekeringsonderwerp]
    - **Huidige situatie:** Beschrijf de huidige dekking
    - **Aandachtspunt/advies/opmerking:** Geef een relevant advies of opmerking
    - **Vraag:** Stel een vraag om de klant te betrekken, bijvoorbeeld of je iets moet uitzoeken of berekenen

    ### 3. Actualisatie van verzekerde sommen of termijnen
    Bij actualisaties, gebruik de volgende structuur:
    - Geef een kort overzicht van de huidige situatie
    - Vraag of dit nog actueel is
    - Geef een toelichting op het advies, indien van toepassing

    ### 4. Standaard aandachtspunten
    Neem de volgende punten op, indien relevant:

    #### Bedrijfsschade
    - Wijs op langere herstelperiodes vanwege:
      - Vergunningsprocedures
      - Schaarste van aannemers
      - Langere bouwtijden

    #### Personeel
    - Vraag of er personeel in dienst is
    - Wijs op mogelijke aanvullende risico's bij personeel in dienst

    #### Goederen en inventaris
    - Leg het onderscheid uit tussen goederen/voorraad en inventaris

    ### 5. Afsluiting
    - Benadruk het belang van reageren op de e-mail of het maken van een belafspraak
    - Nodig de klant uit om vragen te stellen
    - Benadruk dat het doel is om de verzekeringen up-to-date te houden

    ## Belangrijke regels
    - Vermijd het benoemen van eigen risico's, tenzij expliciet gevraagd
    - Ga er niet vanuit dat de klant ergens niet voor verzekerd is; ze kunnen elders verzekerd zijn
    - Noem specifieke risico's en geef concrete voorbeelden, vermijd algemene beschrijvingen
    - Gebruik de lijst van beschikbare verzekeringen bij Veldhuis Advies: {verzekeringen}

    ## Productbeschrijvingen
    Gebruik de volgende productbeschrijvingen bij het bespreken van de huidige verzekeringen en aanbevelingen:

    {product_descriptions}

    Gebruik de volgende informatie:

    Transcript:
    {transcript}

    Huidige dekking:
    {current_coverage}

    Geselecteerde aanbevelingen:
    {selected_recommendations}

    Genereer nu een e-mail volgens bovenstaande richtlijnen.
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o-2024-08-06", temperature=0.5)
    feedback_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o-mini", temperature=0.5)

    try:
        st.markdown("**Denken...**")
        prompt_template = ChatPromptTemplate.from_template(prompt)
        
        st.markdown("**Schrijven...**")
        chain = prompt_template | chat_model | StrOutputParser()
        result = chain.invoke({
            "product_descriptions": json.dumps(product_descriptions, ensure_ascii=False, indent=2),
            "transcript": transcript,
            "current_coverage": current_coverage_str,
            "selected_recommendations": json.dumps(selected_recommendations, ensure_ascii=False, indent=2),
            "verzekeringen": ", ".join(st.secrets.get("VERZEKERINGEN", []))
        })

        st.markdown("**Feedback loop...**")
        feedback_prompt = """
        Beoordeel de volgende e-mail op basis van de gegeven richtlijnen. Controleer of:
        1. Alle instructies zijn gevolgd
        2. Alle informatie feitelijk correct is
        3. De toon passend is voor een verzekeringsadvies
        4. De productbeschrijvingen correct zijn gebruikt

        E-mail:
        {email}

        Geef puntsgewijs feedback en suggesties voor verbetering.
        """
        feedback_chain = LLMChain(llm=feedback_model, prompt=ChatPromptTemplate.from_template(feedback_prompt))
        feedback = feedback_chain.run(email=result)

        st.markdown("**Verbeterde versie schrijven...**")
        improvement_prompt = """
        Verbeter de volgende e-mail op basis van de gegeven feedback:

        Originele e-mail:
        {original_email}

        Feedback:
        {feedback}

        Schrijf een verbeterde versie van de e-mail.
        """
        improvement_chain = LLMChain(llm=chat_model, prompt=ChatPromptTemplate.from_template(improvement_prompt))
        improved_result = improvement_chain.run(original_email=result, feedback=feedback)

        return improved_result
    except Exception as e:
        logger.error(f"Error in generate_email: {str(e)}")
        raise e