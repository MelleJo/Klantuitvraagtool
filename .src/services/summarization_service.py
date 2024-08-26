import json
import logging
import os
import traceback
from typing import List, Dict, Any
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from config import (
    OPENAI_MODEL, OPENAI_TEMPERATURE, FEEDBACK_MODEL, FEEDBACK_TEMPERATURE,
    LOG_FILE, LOG_LEVEL, PRODUCT_DESCRIPTIONS_FILE, INSURANCE_ADVISOR_PROMPT_FILE
)

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

def load_product_descriptions() -> Dict[str, Any]:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(project_root, PRODUCT_DESCRIPTIONS_FILE)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{PRODUCT_DESCRIPTIONS_FILE}' was not found at {json_path}.")
    except json.JSONDecodeError:
        raise ValueError(f"The file '{PRODUCT_DESCRIPTIONS_FILE}' contains invalid JSON.")

def get_product_description(product_name: str, product_descriptions: Dict[str, Any]) -> str:
    for category, products in product_descriptions.items():
        if product_name.lower() in products:
            return products[product_name.lower()]['description']
    return "Geen specifieke productbeschrijving beschikbaar."

def analyze_transcript(transcript: str) -> Dict[str, Any]:
    with open(INSURANCE_ADVISOR_PROMPT_FILE, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
    
    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)

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
    
    if current_recommendation:
        result['recommendations'].append(current_recommendation)
    
    logger.info(f"Parsed result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result

def couple_coverage_with_descriptions(current_coverage: List[str], product_descriptions: Dict[str, Any]) -> List[Dict[str, str]]:
    enhanced_coverage = []
    for item in current_coverage:
        for category, products in product_descriptions.items():
            for product, details in products.items():
                if product.lower() in item.lower():
                    enhanced_coverage.append({
                        "coverage": item,
                        "description": details.get("description", ""),
                        "title": details.get("title", product)
                    })
                    break
            else:
                continue
            break
        else:
            enhanced_coverage.append({
                "coverage": item,
                "description": "Geen specifieke productbeschrijving beschikbaar.",
                "title": "Onbekende verzekering"
            })
    return enhanced_coverage

def generate_email(transcript: str, enhanced_coverage: List[Dict[str, str]], selected_recommendations: List[Dict[str, Any]]) -> str:
    product_descriptions = load_product_descriptions()
    enhanced_coverage_str = json.dumps(enhanced_coverage, ensure_ascii=False, indent=2)

    guidelines = """
    # Verzekeringsadvies E-mail Richtlijnen

    1. Begin direct met je naam en functie bij Veldhuis Advies
    2. Gebruik een informele, persoonlijke toon (je/jij), tenzij het transcript aangeeft dat formeel taalgebruik (u) nodig is
    3. Vermijd een uitgebreide introductie of samenvatting aan het begin
    4. Gebruik de gegeven productbeschrijvingen bij het uitleggen van de huidige situatie
    5. Geef concrete, specifieke adviezen gebaseerd op de situatie van de klant
    6. Stel bij elk onderwerp een relevante vraag om de klant te betrekken
    7. Vermijd het noemen van eigen risico's of veronderstellen dat de klant ergens niet voor verzekerd is
    8. Gebruik korte, krachtige zinnen en paragrafen
    9. Sluit af met een beknopte, vriendelijke uitnodiging om te reageren
    10. Vermeld altijd het telefoonnummer 0578-699760
    11. Maak geen aannames over wanneer verzekeringen voor het laatst zijn gewijzigd
    12. Gebruik geen termen als "profiteren" bij het beschrijven van verzekeringssituaties
    13. Integreer de officiële productbeschrijvingen naadloos in de uitleg van de huidige situatie
    14. Geef een korte uitleg over waarom bepaalde wijzigingen of toevoegingen aan de verzekering voordelig kunnen zijn
    15. Vraag bij elke aanbeveling of de klant een berekening wil ontvangen voor premievergelijking
    16. Vermeld bij de arbeidsongeschiktheidsverzekering dat dit gebaseerd is op de gegevens bij Veldhuis Advies
    """

    prompt = f"""
    {guidelines}

    Schrijf een e-mail met de volgende structuur:

    1. Openingszin met naam en functie
    2. Voor elke relevante verzekering in de huidige dekking:
       - Naam verzekering (in bold)
       - Huidige situatie: Beschrijf kort de dekking, gebruik hierbij de gegeven productbeschrijving
       - Advies: Geef een concreet advies of aandachtspunt, gebaseerd op de huidige situatie en mogelijke risico's. Leg uit waarom dit advies voordelig kan zijn.
       - Vraag: Stel een relevante vraag om de klant te betrekken, inclusief een aanbod om een berekening te maken voor premievergelijking

    3. Eventuele overige aandachtspunten (bijv. over personeel of specifieke risico's)
    4. Korte, vriendelijke afsluiting met verzoek om reactie en contactgegevens

    Gebruik de volgende informatie:

    Transcript:
    {transcript}

    Huidige dekking (met productbeschrijvingen):
    {enhanced_coverage_str}

    Geselecteerde aanbevelingen:
    {json.dumps(selected_recommendations, ensure_ascii=False, indent=2)}

    Beschikbare verzekeringen bij Veldhuis Advies:
    {", ".join(st.secrets.get("VERZEKERINGEN", []))}

    Productbeschrijvingen:
    {json.dumps(product_descriptions, ensure_ascii=False, indent=2)}

    Genereer nu een e-mail volgens bovenstaande richtlijnen en structuur.
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)
    feedback_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model=FEEDBACK_MODEL, temperature=FEEDBACK_TEMPERATURE)

    try:
        logging.info("Starting email generation")
        prompt_template = ChatPromptTemplate.from_template(prompt)
        
        chain = prompt_template | chat_model | StrOutputParser()
        result = chain.invoke({
            "transcript": transcript,
            "enhanced_coverage": enhanced_coverage_str,
            "selected_recommendations": json.dumps(selected_recommendations, ensure_ascii=False, indent=2),
            "verzekeringen": ", ".join(st.secrets.get("VERZEKERINGEN", [])),
            "product_descriptions": json.dumps(product_descriptions, ensure_ascii=False, indent=2)
        })
        logging.info("Initial email generated")
        logging.debug(f"Initial email content: {result}")

        feedback_prompt = f"""
        {guidelines}

        Beoordeel de volgende e-mail op basis van de bovenstaande richtlijnen. Controleer specifiek of:

        1. De e-mail direct begint met naam en functie, zonder uitgebreide introductie
        2. De toon persoonlijk en informeel is (tenzij anders aangegeven in het transcript)
        3. Productbeschrijvingen goed zijn geïntegreerd in de uitleg van de huidige situatie
        4. Adviezen concreet en specifiek zijn voor de situatie van de klant, met uitleg waarom ze voordelig kunnen zijn
        5. Er bij elk onderwerp een relevante vraag wordt gesteld, inclusief een aanbod voor premieberekening
        6. De afsluiting kort en vriendelijk is, met een duidelijke uitnodiging om te reageren
        7. Het telefoonnummer 0578-699760 is vermeld
        8. Er geen aannames worden gemaakt over wanneer verzekeringen voor het laatst zijn gewijzigd
        9. Termen als "profiteren" worden vermeden bij het beschrijven van verzekeringssituaties
        10. Bij de arbeidsongeschiktheidsverzekering wordt vermeld dat dit gebaseerd is op de gegevens bij Veldhuis Advies

        E-mail:
        {result}

        Geef puntsgewijs feedback en suggesties voor verbetering.
        """
        feedback_chain = LLMChain(llm=feedback_model, prompt=ChatPromptTemplate.from_template(feedback_prompt))
        feedback = feedback_chain.run(email=result)
        logging.info("Feedback generated")
        logging.debug(f"Feedback content: {feedback}")

        improvement_prompt = f"""
        {guidelines}

        Verbeter de volgende e-mail op basis van de gegeven feedback en de bovenstaande richtlijnen. Zorg ervoor dat:

        1. De e-mail voldoet aan alle genoemde richtlijnen
        2. De toon consistent persoonlijk en informeel blijft (tenzij anders aangegeven)
        3. Productbeschrijvingen naadloos zijn geïntegreerd
        4. Adviezen concreet en relevant zijn, met uitleg waarom ze voordelig kunnen zijn
        5. Elke sectie een duidelijke vraag bevat, inclusief een aanbod voor premieberekening
        6. De e-mail bondig en to-the-point blijft
        7. De afsluiting kort en uitnodigend is
        8. Er geen aannames worden gemaakt over wanneer verzekeringen voor het laatst zijn gewijzigd
        9. Termen als "profiteren" worden vermeden bij het beschrijven van verzekeringssituaties
        10. Bij de arbeidsongeschiktheidsverzekering wordt vermeld dat dit gebaseerd is op de gegevens bij Veldhuis Advies

        Originele e-mail:
        {result}

        Feedback:
        {feedback}

        Schrijf een verbeterde versie van de e-mail.
        """
        improvement_chain = LLMChain(llm=chat_model, prompt=ChatPromptTemplate.from_template(improvement_prompt))
        improved_result = improvement_chain.run(original_email=result, feedback=feedback)
        logging.info("Improved email generated")
        logging.debug(f"Improved email content: {improved_result}")

        return improved_result
    except Exception as e:
        logging.error(f"Error in generate_email: {str(e)}")
        raise e