print("Starting summarization_service.py")

try:
    import json
    print("Successfully imported json")
except ImportError as e:
    print(f"Failed to import json: {e}")

try:
    import logging
    from typing import List, Dict, Any
    import streamlit as st
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from utils.text_processing import load_prompt
    import traceback
    print("Successfully imported all other modules")
except ImportError as e:
    print(f"Failed to import a module: {e}")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("Finished importing modules in summarization_service.py")
print("summarization_service.py is being executed")

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
        
        #logger.debug(f"Parsed analysis result: {json.dumps(parsed_result, indent=2)}")
        
        if not isinstance(parsed_result, dict):
            raise ValueError(f"Expected dictionary, got {type(parsed_result)}")
        
        if 'recommendations' not in parsed_result or parsed_result['recommendations'] is None:
            logger.warning("No recommendations found in parsed result")
            parsed_result['recommendations'] = []
        
        logger.info(f"Number of recommendations: {len(parsed_result['recommendations'])}")
        for i, rec in enumerate(parsed_result['recommendations']):
            logger.info(f"Recommendation {i+1}: {rec.get('title', 'No title')}")
        
        # Store the parsed result in the session state
        st.session_state.state['suggestions'] = parsed_result
        logger.debug("Stored parsed result in session state")
        #logger.debug(f"Session state after storing suggestions: {json.dumps(st.session_state.state, default=str)}")
        
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
            if line.startswith('<aanbeveling>'):
                current_recommendation = {'title': '', 'description': '', 'rechtvaardiging': '', 'specific_risks': []}
            elif line.startswith('<rechtvaardiging>'):
                current_recommendation['rechtvaardiging'] = ''
            elif line.startswith('<bedrijfsspecifieke_risicos>'):
                pass  # We'll handle specific risks in the else clause
            elif line.startswith('</aanbeveling>'):
                if current_recommendation:
                    result['recommendations'].append(current_recommendation)
                    logger.debug(f"Appending recommendation: {current_recommendation}")
                current_recommendation = None
            elif current_recommendation:
                if not current_recommendation['title']:
                    current_recommendation['title'] = line
                elif not current_recommendation['description']:
                    current_recommendation['description'] = line
                elif not current_recommendation['rechtvaardiging']:
                    current_recommendation['rechtvaardiging'] = line
                else:
                    current_recommendation['specific_risks'].append(line)
        elif current_section and line and not line.startswith('<') and not line.startswith('>'):
            result[current_section].append(line)
    
    if current_recommendation:
        result['recommendations'].append(current_recommendation)
    
    logger.info(f"Number of recommendations parsed: {len(result['recommendations'])}")
    for i, rec in enumerate(result['recommendations']):
        logger.info(f"Recommendation {i+1}: {rec['title']}")
    
    return result

def generate_email(transcript: str, analysis: Dict[str, Any], selected_recommendations: List[str]) -> str:
    prompt = f"""
    Je bent een verzekeringsadviseur die een e-mail schrijft aan een klant als onderdeel van je zorgplicht.
    Het doel is om de huidige situatie van de klant te verifiëren en advies te geven over mogelijke verbeteringen in hun verzekeringsdekking.
    Schrijf een professionele en vriendelijke e-mail die het volgende bevat:

    1. Een korte introductie waarin je uitlegt waarom je contact opneemt (zorgplicht, periodieke check).
    2. Een samenvatting van hun huidige dekking, gebaseerd op de analyse.
    3. Een overzicht van de geïdentificeerde dekkingshiaten en waarom deze belangrijk zijn voor de klant.
    4. Je verzekeringsaanbevelingen, met uitleg waarom deze belangrijk zijn voor de specifieke bedrijfssituatie van de klant. Gebruik alleen de geselecteerde aanbevelingen.
    5. Een uitnodiging voor een vervolgafspraak om de situatie en eventuele aanpassingen te bespreken.

    Gebruik de volgende informatie:

    Transcript:
    {{transcript}}

    Analyse:
    {{analysis}}

    Geselecteerde aanbevelingen:
    {{selected_recommendations}}

    Zorg ervoor dat de e-mail de nadruk legt op onze zorgplicht en het belang van het up-to-date houden van de verzekeringssituatie van de klant.
    De e-mail moet in het Nederlands zijn en verwijzen naar Nederlandse verzekeringsproducten.
    Gebruik geen placeholders zoals [Klantnaam] of [Uw Naam], maar verwijs naar de klant en jezelf op een algemene manier.
    """

    chat_model = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o", temperature=0.3)

    try:
        # Filter the recommendations to include only the selected ones
        filtered_analysis = analysis.copy()
        filtered_analysis['recommendations'] = [rec for rec in analysis['recommendations'] if rec['title'] in selected_recommendations]

        prompt_template = ChatPromptTemplate.from_template(prompt)
        chain = prompt_template | chat_model
        result = chain.invoke({
            "transcript": transcript,
            "analysis": json.dumps(filtered_analysis, ensure_ascii=False, indent=2),
            "selected_recommendations": json.dumps(selected_recommendations, ensure_ascii=False, indent=2)
        })
        return result.content
    except Exception as e:
        logger.error(f"Error in generate_email: {str(e)}")
        raise e