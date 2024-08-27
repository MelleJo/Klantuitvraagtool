import autogen
from typing import Dict, Any, List
import streamlit as st
import logging
import json
import os
import streamlit as st

os.environ["AUTOGEN_USE_DOCKER"] = "0"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI config
config_list = [
    {
        'model': 'gpt-4o-2024-08-06',
        'api_key': st.secrets["OPENAI_API_KEY"],
        'temperature': 0.1
    }
]

# Define agents
user_proxy = autogen.UserProxyAgent(
    name="User",
    system_message="A human user interacting with the insurance advisor system.",
    human_input_mode="NEVER"
)

transcript_analyst = autogen.AssistantAgent(
    name="TranscriptAnalyst",
    system_message="""You are an expert in analyzing insurance-related transcripts. Your role is to extract key information about the client's current coverage and potential needs. Provide your analysis in the following format:

    <analyse>
    <bestaande_dekking>
    [List current insurance policies, one per line]
    </bestaande_dekking>

    <dekkingshiaten>
    [List identified coverage gaps, one per line]
    </dekkingshiaten>

    <verzekeringsaanbevelingen>
    [For each recommendation, include:]
    <aanbeveling>
    Aanbeveling: [Title of the recommendation]
    Beschrijving: [Describe the recommended insurance]
    Rechtvaardiging: [Explain why this insurance is important for specifically this client, based on any info you can derrive out of the transcript or based on the client's business type]
    Specifieke risico's:
    - [Describe specific risk 1]
    - [Describe specific risk 2]
    - [Add more risks if needed]
    </aanbeveling>
    [Repeat for each recommendation]
    </verzekeringsaanbevelingen>

    <aanvullende_opmerkingen>
    [List any assumptions or unclear points, one per line]
    </aanvullende_opmerkingen>
    </analyse>
    """,
    human_input_mode="NEVER",
    llm_config={"config_list": config_list},
    max_consecutive_auto_reply=3
)

recommendation_agent = autogen.AssistantAgent(
    name="RecommendationAgent",
    system_message="You are an expert in insurance products and generating tailored recommendations. Your role is to suggest appropriate insurance products based on the client's needs and current coverage.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3
)

email_generator = autogen.AssistantAgent(
    name="EmailGenerator",
    system_message="You are an expert in crafting personalized and professional emails. Your role is to create a client-friendly email summarizing the insurance analysis and recommendations.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3
)

quality_control = autogen.AssistantAgent(
    name="QualityControl",
    system_message="You are responsible for reviewing and improving the outputs from other agents. Ensure all content is accurate, professional, and tailored to the client's needs.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3
)

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
                current_recommendation = None
            if line.startswith('</verzekeringsaanbevelingen>'):
                current_section = None
        elif current_section == 'recommendations':
            if line.startswith('Aanbeveling:'):
                if current_recommendation:
                    result['recommendations'].append(current_recommendation)
                current_recommendation = {'title': line[12:].strip(), 'description': '', 'rechtvaardiging': '', 'specific_risks': []}
            elif line.startswith('Beschrijving:'):
                current_recommendation['description'] = line[12:].strip()
            elif line.startswith('Rechtvaardiging:'):
                current_recommendation['rechtvaardiging'] = line[16:].strip()
            elif line.startswith('Specifieke risico\'s:'):
                continue
            elif current_recommendation:
                if not current_recommendation['specific_risks'] or current_recommendation['specific_risks'][-1].startswith('-'):
                    current_recommendation['specific_risks'].append(line)
                else:
                    current_recommendation['specific_risks'][-1] += ' ' + line
        elif current_section and line and not line.startswith('<'):
            result[current_section].append(line)

    if current_recommendation:
        result['recommendations'].append(current_recommendation)

    return result

def load_product_descriptions() -> Dict[str, Any]:
    product_descriptions_file = os.path.join(os.path.dirname(__file__), '..', '.src', 'product_descriptions.json')
    try:
        with open(product_descriptions_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Product descriptions file not found at {product_descriptions_file}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in product descriptions file: {str(e)}")
        return {}

def analyze_transcript(transcript: str) -> Dict[str, Any]:
    try:
        logger.info("Starting transcript analysis")
        
        user_proxy.initiate_chat(
            transcript_analyst,
            message=f"Please analyze this insurance-related transcript:\n\n{transcript}",
            summary_method="last_msg",
            max_turns=1
        )
        
        analysis = transcript_analyst.last_message()["content"]
        logger.info("Transcript analysis completed")
        
        parsed_result = parse_analysis_result(analysis)
        
        return parsed_result
    except Exception as e:
        logger.error(f"Error in analyze_transcript: {str(e)}", exc_info=True)
        return {"error": str(e)}

import json
import logging
from typing import List, Dict, Any

def generate_email(transcript: str, enhanced_coverage: str, selected_recommendations: str, max_retries: int = 3) -> str:
    try:
        enhanced_coverage_list = json.loads(enhanced_coverage)
        selected_recommendations_list = json.loads(selected_recommendations)
        
        current_coverage = "\n".join([f"{item.get('title', 'Onbekende verzekering')}: {item.get('coverage', 'Geen details beschikbaar')}" for item in enhanced_coverage_list])

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

        email_structure = """
        Schrijf een e-mail met de volgende structuur:

        1. Openingszin met naam en functie
        2. Voor elke relevante verzekering in de huidige dekking:
           - Naam verzekering (in bold)
           - Huidige situatie: Beschrijf kort de dekking, gebruik hierbij de gegeven productbeschrijving
           - Advies: Geef een concreet advies of aandachtspunt, gebaseerd op de huidige situatie en mogelijke risico's. Leg uit waarom dit advies voordelig kan zijn.
           - Vraag: Stel een relevante vraag om de klant te betrekken, inclusief een aanbod om een berekening te maken voor premievergelijking

        3. Eventuele overige aandachtspunten (bijv. over personeel of specifieke risico's)
        4. Korte, vriendelijke afsluiting met verzoek om reactie en contactgegevens
        """

        for attempt in range(max_retries):
            try:
                # Step 1: Generate initial email
                user_proxy.initiate_chat(
                    email_generator,
                    message=f"""
                    {guidelines}
                    {email_structure}
                    
                    Gebruik de volgende informatie:
                    
                    Huidige dekking:
                    {current_coverage}
                    Transcript: {transcript}
                    Geselecteerde aanbevelingen: {json.dumps(selected_recommendations_list, ensure_ascii=False)}

                    Genereer nu een e-mail volgens bovenstaande richtlijnen en structuur. Zorg ervoor dat de e-mail volledig is en alle gevraagde elementen bevat.
                    """
                )
                
                initial_email = email_generator.last_message().get("content", "")
                if not initial_email.strip():
                    raise ValueError("Initial email generation returned empty content.")
                
                logging.info(f"Initial email generated (Attempt {attempt + 1})")
                logging.debug(f"Initial email content: {initial_email[:500]}...")  # Log first 500 chars

                # Step 2: Generate feedback
                user_proxy.initiate_chat(
                    quality_control,
                    message=f"""
                    {guidelines}

                    Beoordeel de volgende e-mail op basis van de bovenstaande richtlijnen. Geef puntsgewijs feedback en suggesties voor verbetering.

                    E-mail:
                    {initial_email}
                    """
                )
                
                feedback = quality_control.last_message().get("content", "")
                if not feedback.strip():
                    raise ValueError("Feedback generation returned empty content.")
                
                logging.info(f"Feedback generated (Attempt {attempt + 1})")
                logging.debug(f"Feedback content: {feedback[:500]}...")  # Log first 500 chars

                # Step 3: Improve email based on feedback
                user_proxy.initiate_chat(
                    email_generator,
                    message=f"""
                    {guidelines}

                    Verbeter de volgende e-mail op basis van de gegeven feedback en de bovenstaande richtlijnen. Zorg ervoor dat de verbeterde e-mail volledig is en alle gevraagde elementen bevat.

                    Originele e-mail:
                    {initial_email}

                    Feedback:
                    {feedback}

                    Schrijf een verbeterde versie van de e-mail.
                    """
                )
                
                improved_email = email_generator.last_message().get("content", "")
                if not improved_email.strip():
                    raise ValueError("Improved email generation returned empty content.")
                
                logging.info(f"Improved email generated (Attempt {attempt + 1})")
                logging.debug(f"Improved email content: {improved_email[:500]}...")  # Log first 500 chars

                return improved_email

            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise

        raise ValueError(f"Failed to generate email after {max_retries} attempts")

    except Exception as e:
        logging.error(f"Error in generate_email: {str(e)}")
        logging.error(f"Error type: {type(e)}")
        logging.error(f"Error args: {e.args}")
        logging.error(f"Transcript: {transcript}")
        logging.error(f"Enhanced coverage: {enhanced_coverage}")
        logging.error(f"Selected recommendations: {selected_recommendations}")
        raise

def load_insurance_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'insurance_advisor_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Insurance advisor prompt file not found at {prompt_path}")
        return ""

def initialize_agents():
    insurance_prompt = load_insurance_prompt()
    transcript_analyst.update_system_message(insurance_prompt)
    logger.info("Agents initialized with insurance advisor prompt")

# Initialize agents when this module is imported
initialize_agents()