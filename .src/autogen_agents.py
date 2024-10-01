import autogen
from typing import Dict, Any, List
import streamlit as st
import logging
import json
import os
import streamlit as st
from openai import OpenAI
from anthropic import Anthropic

os.environ["AUTOGEN_USE_DOCKER"] = "0"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def identify_risks_and_questions(transcript: str) -> Dict[str, List[str]]:
    try:
        prompt = f"""
        Analyze the following insurance advisor's transcript and identify:
        1. Potential risks that the client may face based on their current coverage and business activities.
        2. Questions that the advisor wants to ask or topics they want to discuss with the client.

        Transcript:
        {transcript}

        Provide your analysis in the following format:
        <analysis>
        <risks>
        - [List each identified risk on a new line]
        </risks>
        <questions>
        - [List each question or topic to discuss on a new line]
        </questions>
        </analysis>
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in insurance risk analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )

        content = response.choices[0].message.content.strip()
        
        # Parse the content
        risks = []
        questions = []
        current_section = None
        for line in content.split('\n'):
            if '<risks>' in line:
                current_section = 'risks'
            elif '<questions>' in line:
                current_section = 'questions'
            elif line.strip().startswith('-') and current_section:
                if current_section == 'risks':
                    risks.append(line.strip()[1:].strip())
                elif current_section == 'questions':
                    questions.append(line.strip()[1:].strip())

        return {
            "identified_risks": risks,
            "questions_to_ask": questions
        }

    except Exception as e:
        logger.error(f"Error in identify_risks_and_questions: {str(e)}")
        return {"error": str(e)}

def load_product_descriptions():
    file_path = os.path.join(os.path.dirname(__file__), '..', '.src', 'product_descriptions.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading product descriptions: {str(e)}")
        return {}

product_descriptions = load_product_descriptions()

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
    Beschrijving: [Describe the recommended insurance, based on {product_descriptions}]
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

def analyze_transcript(transcript: str) -> Dict[str, Any]:
    try:
        logger.info("Starting transcript analysis")
        
        # Existing analysis
        user_proxy.initiate_chat(
            transcript_analyst,
            message=f"""Please analyze this insurance-related transcript and identify the relevant insurance types:

{transcript}

In your analysis, include a list of identified insurance types at the end.""",
            summary_method="last_msg",
            max_turns=1
        )
        
        analysis = transcript_analyst.last_message()["content"]
        logger.info("Transcript analysis completed")
        
        parsed_result = parse_analysis_result(analysis)
        
        # New risk and question identification
        risks_and_questions = identify_risks_and_questions(transcript)
        
        # Combine results
        parsed_result.update(risks_and_questions)
        
        return parsed_result
    except Exception as e:
        logger.error(f"Error in analyze_transcript: {str(e)}", exc_info=True)
        return {"error": str(e)}

def load_guidelines() -> str:
    file_path = os.path.join(os.path.dirname(__file__), '..', '.src', 'guidelines.txt')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error loading guidelines: {str(e)}")
        return ""

def load_insurance_specific_instructions(identified_insurances: List[str]) -> Dict[str, str]:
    instructions = {}
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(current_file_path)
    guidelines_dir = os.path.join(project_root, 'src', 'insurance_guidelines')
    
    for insurance in identified_insurances:
        file_path = os.path.join(guidelines_dir, f"{insurance}.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                instructions[insurance] = file.read()
        else:
            logging.warning(f"Specific instructions file not found for insurance type: {insurance}")
    
    return instructions

def generate_email(transcript: str, enhanced_coverage: str, selected_recommendations: str, identified_insurances: List[str]) -> Dict[str, str]:
    try:
        enhanced_coverage_list = json.loads(enhanced_coverage)
        selected_recommendations_list = json.loads(selected_recommendations)
        product_descriptions = load_product_descriptions()
        guidelines = load_guidelines()
        insurance_specific_instructions = load_insurance_specific_instructions(identified_insurances)

        prompt = f"""
        Generate an email based on the following information:

        Transcript: {transcript}

        Current Coverage and Analysis: {json.dumps(enhanced_coverage_list, indent=2)}

        Selected Recommendations: {json.dumps(selected_recommendations_list, indent=2)}

        Use the following specific instructions for each identified insurance type:

        {json.dumps(insurance_specific_instructions, indent=2)}

        Product Descriptions:
        {json.dumps(product_descriptions, indent=2)}

        General Guidelines:
        {guidelines}

        Ensure that you address each identified insurance type using its specific instructions.
        The email should be structured, personalized, and follow all the general email writing guidelines provided.
        Focus on the identified insurance types and the selected recommendations.
        
        Crucial points to include:
        1. Use dashes (-) instead of bullet points for all lists.
        2. For inventory and goods insurance, always explain the difference: "Inventaris omvat zaken zoals de inrichting van je bedrijf en machines, terwijl goederen betrekking hebben op handelswaren."
        3. Mention at least once that Veldhuis Advies is an intermediary: "Als tussenpersoon helpt Veldhuis Advies je bij het vinden van de beste verzekeringen voor jouw situatie."
        4. For each insurance type, provide a detailed explanation and clearly state the consequences of underinsurance or insufficient coverage.
        5. For liability insurance (AVB), always discuss the "opzicht" clause and its relevance.
        6. For business interruption insurance, always explain why recovery times might be longer nowadays due to material shortages, staff shortages, and longer delivery times.
        7. For home insurance, always mention factors like solar panels, swimming pools, and renovations that can affect coverage.
        8. Avoid double questions - ask for information or changes only once per topic.
        9. Format all placeholders in all caps with square brackets, e.g., [KLANTNAAM].
        10. Provide specific examples of how each insurance type protects the client's business or personal assets.

        The email should be comprehensive yet easy to read, with each insurance type clearly separated and explained.
        """

        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are an experienced insurance advisor at Veldhuis Advies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=14000
        )

        initial_email_content = response.choices[0].message.content.strip()
        
        if not initial_email_content:
            raise ValueError("Email generation returned empty content.")

        # Apply correction AI
        corrected_email = correction_AI(initial_email_content, guidelines)

        logging.info("Email generated and corrected successfully")
        logging.debug(f"Initial email content: {initial_email_content[:500]}...")
        logging.debug(f"Corrected email content: {corrected_email[:500]}...")

        return {
            "initial_email": initial_email_content,
            "corrected_email": corrected_email
        }

    except Exception as e:
        logging.error(f"Error in generate_email: {str(e)}")
        logging.error(f"Error type: {type(e)}")
        logging.error(f"Error args: {e.args}")
        logging.error(f"Transcript: {transcript}")
        logging.error(f"Enhanced coverage: {enhanced_coverage}")
        logging.error(f"Selected recommendations: {selected_recommendations}")
        logging.error(f"Identified insurances: {identified_insurances}")
        raise


def correction_AI(email_content: str, guidelines: str) -> str:
    try:
        prompt = f"""
        Review and correct the following email content based on these guidelines:

        Guidelines:
        {guidelines}

        Email Content:
        {email_content}

        Please provide the corrected version of the email, ensuring it adheres to all guidelines. Pay special attention to:
        1. Using dashes (-) instead of bullet points for all lists.
        2. Including a detailed explanation of the difference between inventory and goods insurance.
        3. Mentioning that Veldhuis Advies is an intermediary.
        4. Providing detailed explanations for each insurance type and stating the consequences of underinsurance or insufficient coverage.
        5. Discussing the "opzicht" clause for liability insurance.
        6. Explaining longer recovery times for business interruption insurance.
        7. Mentioning factors like solar panels, swimming pools, and renovations for home insurance.
        8. Avoiding double questions.
        9. Formatting all placeholders in all caps with square brackets.
        10. Providing specific examples for each insurance type.

        Ensure the email is comprehensive yet easy to read, with each insurance type clearly separated and explained.
        """

        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are an AI assistant that specializes in correcting and improving insurance advice emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=14000
        )

        corrected_email = response.choices[0].message.content.strip()

        if not corrected_email:
            raise ValueError("Correction AI returned empty content.")

        return corrected_email

    except Exception as e:
        logging.error(f"Error in correction_AI: {str(e)}")
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