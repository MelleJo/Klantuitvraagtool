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

def get_insurance_info(insurance_type: str, product_descriptions: Dict[str, Any]) -> Dict[str, Any]:
    for category, products in product_descriptions.items():
        if isinstance(products, dict):
            if insurance_type in products:
                return products[insurance_type]
            for product, details in products.items():
                if insurance_type.lower() in product.lower():
                    return details
    return {} 


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
            temperature=0.2
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

def generate_detailed_explanation(insurance_type: str, transcript: str, product_descriptions: Dict[str, Any]) -> str:
    insurance_info = get_insurance_info(insurance_type, product_descriptions)
    
    if not insurance_info:
        return f"Geen gedetailleerde informatie beschikbaar voor {insurance_type}."

    prompt = f"""
    Gegeven de volgende informatie over {insurance_type}:

    Titel: {insurance_info.get('title', 'Niet gespecificeerd')}
    Beschrijving: {insurance_info.get('description', 'Geen beschrijving beschikbaar')}
    Belangrijke punten: {', '.join(insurance_info.get('key_points', ['Niet gespecificeerd']))}
    Veelvoorkomende risico's: {', '.join(insurance_info.get('common_risks', ['Niet gespecificeerd']))}

    En de volgende informatie over de klant:

    {transcript}

    Genereer een gedetailleerde uitleg over deze verzekering, specifiek toegespitst op de situatie van de klant. 
    Includeer:
    1. Een korte introductie van de verzekering
    2. Waarom deze verzekering belangrijk is voor deze specifieke klant
    3. Twee tot drie op maat gemaakte voorbeelden die relevant zijn voor de klant's situatie. Deze voorbeelden MOETEN gebaseerd zijn op de informatie in de klant-transcript en NIET op de generieke voorbeelden.
    4. Drie tot vier risico's of aandachtspunten specifiek voor deze klant, gebaseerd op de informatie in de transcript. Gebruik de "common_risks" alleen als inspiratie, niet als directe bron.
    5. Een afsluitende zin of vraag om de klant aan te moedigen hier meer over na te denken

    Zorg dat de uitleg persoonlijk, informatief en overtuigend is, zonder pusherig over te komen. Gebruik ALLEEN informatie uit de klant-transcript voor specifieke details en voorbeelden.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Je bent een ervaren verzekeringsadviseur die gedetailleerde, op maat gemaakte uitleg geeft over verzekeringen, specifiek gebaseerd op de situatie van de klant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


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
        'advisor_questions': [],
        'ai_risks': [],
        'recommendations': []
    }

    current_section = None
    current_recommendation = None
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('<huidige_dekking>'):
            current_section = 'current_coverage'
        elif line.startswith('<adviseur_vragen>'):
            current_section = 'advisor_questions'
        elif line.startswith('<ai_risicos>'):
            current_section = 'ai_risks'
        elif line.startswith('<aanbevelingen>'):
            current_section = 'recommendations'
        elif line.startswith('</'):
            if current_recommendation:
                result['recommendations'].append(current_recommendation)
                current_recommendation = None
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
            elif current_recommendation and line.startswith('-'):
                current_recommendation['specific_risks'].append(line[1:].strip())
        elif current_section and line and not line.startswith('<'):
            result[current_section].append(line)

    if current_recommendation:
        result['recommendations'].append(current_recommendation)

    return result

def analyze_transcript(transcript: str) -> Dict[str, Any]:
    try:
        logger.info("Starting transcript analysis")
        
        prompt = f"""
        Analyseer het volgende verzekeringstranscript en identificeer:
        1. De huidige dekking van de klant
        2. Vragen en opmerkingen die de adviseur heeft gemaakt
        3. Aanvullende risico's en aandachtspunten die de AI heeft geïdentificeerd, maar de adviseur niet expliciet heeft genoemd

        Transcript:
        {transcript}

        Geef je analyse in het volgende format:
        <analyse>
        <huidige_dekking>
        - [Lijst van huidige verzekeringen, één per regel]
        </huidige_dekking>

        <adviseur_vragen>
        - [Lijst van vragen en opmerkingen van de adviseur, één per regel]
        </adviseur_vragen>

        <ai_risicos>
        - [Lijst van aanvullende risico's en aandachtspunten geïdentificeerd door de AI, één per regel]
        </ai_risicos>
        </analyse>

        Zorg ervoor dat alle informatie in het Nederlands is.
        """

        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Je bent een AI-assistent gespecialiseerd in het analyseren van verzekeringstranscripten."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        analysis = response.choices[0].message.content.strip()
        logger.info("Transcript analysis completed")
        
        parsed_result = parse_analysis_result(analysis)
        
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

def generate_email(transcript: str, enhanced_coverage: str, selected_recommendations: str, identified_insurances: List[str], product_descriptions: Dict[str, Any], detailed_descriptions: str, insurance_specific_instructions: Dict[str, str]) -> Dict[str, str]:
    try:
        enhanced_coverage_list = json.loads(enhanced_coverage)
        selected_recommendations_list = json.loads(selected_recommendations)
        detailed_descriptions_dict = json.loads(detailed_descriptions)
        
        detailed_explanations = {}
        for insurance in identified_insurances:
            detailed_explanations[insurance] = generate_detailed_explanation(insurance, transcript, product_descriptions, insurance_specific_instructions.get(insurance, ""))

        prompt = f"""
        You are tasked with generating a comprehensive and personalized email based on insurance information provided. Follow these instructions carefully to create an effective and tailored communication:

        1. Review the following information:

        <transcript>
        {transcript}
        </transcript>

        <current_coverage_and_analysis>
        {json.dumps(enhanced_coverage_list, indent=2)}
        </current_coverage_and_analysis>

        <selected_recommendations>
        {json.dumps(selected_recommendations_list, indent=2)}
        </selected_recommendations>

        <detailed_explanations>
        {json.dumps(detailed_explanations, indent=2)}
        </detailed_explanations>

        <detailed_descriptions>
        {json.dumps(detailed_descriptions_dict, indent=2)}
        </detailed_descriptions>

        <insurance_specific_instructions>
        {json.dumps(insurance_specific_instructions, indent=2)}
        </insurance_specific_instructions>

        2. Generate an email using the provided information. The email should be structured, personalized, and adhere to the following guidelines:

        a) Begin with a personalized opening, addressing the client directly and introducing yourself as the advisor.
        b) Organize the content into clear, well-labeled sections for each insurance type or recommendation.
        c) Use the detailed explanations to provide comprehensive information about each selected insurance type.
        d) Ensure that all examples and risks mentioned are specifically tailored to the client's situation as described in the transcript.
        e) For each selected insurance type, provide a detailed explanation and clearly state the consequences of underinsurance or insufficient coverage.
        f) Compare current and proposed insurers or coverage options when relevant, explaining the benefits of recommended changes.
        g) Avoid using overly technical terms or jargon. If technical terms are necessary, include brief explanations.
        h) Provide a summarized, easy-to-read breakdown of costs and benefits for each selected insurance type or recommendation.
        i) End each section with a clear call to action, such as offering to provide more information or asking if the client wants to make changes.
        j) Close the email on a polite, friendly note, offering support if needed and thanking the client for their time.

        3. Crucial points to include:

        - Use dashes (-) instead of bullet points for all lists.
        - For inventory and goods insurance, always explain the difference: "Inventaris omvat zaken zoals de inrichting van je bedrijf en machines, terwijl goederen betrekking hebben op handelswaren."
        - For liability insurance (AVB), always discuss the "opzicht" clause and its relevance for both main and secondary activities. Only mention coverage for items under temporary care if the "opzicht" clause is explicitly mentioned in the transcript.
        - For business interruption insurance, always explain why recovery times might be longer nowadays due to material shortages, staff shortages, and longer delivery times.
        - For home insurance, always mention factors like solar panels, swimming pools, and renovations that can affect coverage.
        - Avoid double questions - ask for information or changes only once per topic.
        - Provide specific examples of how each selected insurance type protects the client's business or personal assets.
        - Use "kan van belang zijn" instead of "cruciaal" when discussing importance.

        4. Additional important points:

        - Mention all specific clauses noted in the transcript (e.g., fire extinguishers, outdoor storage, electrical installation).
        - Address any potential need for insurance during furniture transport if mentioned in the transcript.
        - Inquire about possible changes in staffing and mention potential need for employee-related insurances.
        - Discuss cyber risks and the client's online presence if mentioned in the transcript.
        - For personal insurances, provide specific advice or questions, especially regarding disability insurance if mentioned.

        5. Formatting and structure:

        - Format all placeholders in all caps with square brackets, e.g., [KLANTNAAM].
        - Ensure the email is comprehensive yet easy to read, with each selected insurance type clearly separated and explained.
        - Use action-oriented language, directing the client toward specific actions or decisions.

        6. Final output:

        Present your generated email within <email> tags. Ensure that the email adheres to all the guidelines, crucial points, and insurance-specific instructions mentioned above, while strictly focusing on the selected recommendations and identified insurances.
        """

        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are an experienced insurance advisor at Veldhuis Advies, creating personalized and detailed advice based on specific client information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        initial_email_content = response.choices[0].message.content.strip()
        
        if not initial_email_content:
            raise ValueError("Email generation returned empty content.")

        return {
            "initial_email": initial_email_content,
            "corrected_email": initial_email_content  # We'll correct this in the wrapper function
        }

    except Exception as e:
        logging.error(f"Error in generate_email: {str(e)}")
        raise

def correction_AI(email_content: str, guidelines: str, product_descriptions: Dict[str, Any], insurance_specific_instructions: Dict[str, str], transcript: str, detailed_descriptions: str) -> str:
    try:
        style_guide = """
        Style Guide and Example:
        
        1. Opening:
        "Mijn naam is [UW NAAM], je verzekeringsadviseur bij Veldhuis Advies. Ik heb recent je verzekeringssituatie doorgenomen en wil graag enkele punten met je bespreken om ervoor te zorgen dat je dekking optimaal aansluit bij je huidige situatie."

        2. For each insurance type:
        a) Start with the comprehensive description from product_descriptions.json (not needed with the autoverzekering) -> make sure to couple the description with an example to the client's business and situation.
        b) Describe the current situation based on the transcript.
        c) Explain potential risks or changes that might affect the coverage.
        d) Provide a clear, action-oriented suggestion within the paragraph. For example:
        "Gezien de leeftijd van je boot, kan de dagwaarde aanzienlijk zijn. Wil je dat ik help bij het bepalen van de huidige waarde? Zo kunnen we samen beoordelen of de huidige dekking nog passend is."

        3. When discussing risks:
        "Het is belangrijk dat de verzekerde bedragen blijven aansluiten bij de werkelijke waarde. Mocht er een aanzienlijke verandering zijn, laat het ons dan weten. Zo voorkomen we dat je onderverzekerd bent, wat kan leiden tot onvolledige vergoeding bij schade."

        4. For complex topics:
        "Als ondernemer met personeel heb je te maken met specifieke risico's, zoals loondoorbetaling bij ziekte. Je huidige verzekering dekt 100% in het eerste jaar en 70% in het tweede jaar, na tien werkdagen. Wil je de details van deze dekking nog eens doornemen om te zien of deze nog optimaal aansluit bij je situatie?"

        5. Closing:
        "Ik hoop dat deze informatie je helpt om een goed beeld te krijgen van je huidige verzekeringssituatie en mogelijke aandachtspunten. Als je vragen hebt of wilt sparren over je verzekeringen, neem dan gerust contact met me op. Ik sta klaar om je te helpen en adviseren.

        Je kunt me bereiken op 0578-699760.

        Met vriendelijke groet,
        [UW NAAM]
        Veldhuis Advies"

        Remember to maintain this style throughout the email, focusing on informing the client about risks and options rather than pushing products. Integrate action-oriented suggestions within paragraphs instead of separate items.
        """

        prompt = f"""You are tasked with reviewing and correcting an email based on specific guidelines, feedback, and a transcript of a conversation with the client. Your goal is to ensure the email adheres to all guidelines while providing comprehensive and client-specific information. Follow these instructions carefully:

        1. Review the following guidelines:
        <guidelines>
        {guidelines}
        </guidelines>

        2. Now, examine the original email content:
        <email_content>
        {email_content}
        </email_content>

        3. Consider the transcript of the conversation with the client:
        <transcript>
        {transcript}
        </transcript>

        4. Take into account the detailed descriptions of recommendations:
        <detailed_descriptions>
        {detailed_descriptions}
        </detailed_descriptions>

        5. Your task is to correct and improve the email content based on the guidelines and the following specific instructions:

        a) Start with a professional introduction stating your name and role.
        b) Group insurances by type: business insurances first, then personal insurances.
        c) For each insurance type:
           - Start with the comprehensive description from product_descriptions.json
           - Provide a clear explanation of the current situation based on the transcript
           - Include client-specific risks and examples
           - Explain consequences of underinsurance or insufficient coverage
           - Offer relevant additional information
           - Include a clear, personalized call-to-action within the paragraph
        d) Avoid abbreviations and explain any technical terms used.
        e) Ensure all relevant details are included for each insurance type.
        f) Increase personalization by referring specifically to the client's situation as described in the transcript.
        g) Provide more detailed explanations of potential risks for each insurance type.
        h) Format all placeholders in all caps with square brackets.

        6. Use the following product descriptions to ensure each insurance product is well described:
        <product_descriptions>
        {json.dumps(product_descriptions, indent=2, ensure_ascii=False)}
        </product_descriptions>

        7. Refer to the insurance-specific guidelines to avoid any violations:
        <insurance_guidelines>
        {json.dumps(insurance_specific_instructions, indent=2, ensure_ascii=False)}
        </insurance_guidelines>

        8. Follow this style guide and example to maintain a consistent tone and structure:
        <style_guide>
        {style_guide}
        </style_guide>

        9. Structure your corrected email as follows:
        a) Professional introduction
        b) Business insurances
        c) Personal insurances
        d) Brief conclusion emphasizing availability for questions and discussion

        10. Ensure the email is comprehensive yet easy to read, with each insurance type clearly separated and explained.

        11. After completing your corrected version, use this checklist for a final review:
           a) Is the opening professional and personalized?
           b) Are all insurance products adequately described using information from the product descriptions?
           c) Are the risks mentioned relevant and specific to the client's business and personal situation?
           d) Are there clear, personalized call-to-actions within each paragraph?
           e) Does the email focus on informing rather than pushing products?
           f) Is the email well-structured and easy to read?
           g) Does the conclusion emphasize availability for further discussion?
           h) Does the writing style match the provided style guide and example?
           i) Are all technical terms explained and abbreviations avoided?
           j) Are all insurances mentioned in the transcript addressed in the email?
           k) Is the difference between inventory and goods clearly explained?
           l) Are all specific clauses mentioned in the transcript (e.g., fire extinguishers, outdoor storage, electrical installation) addressed?
           m) Is the "opzicht" clause for liability insurance correctly explained and only mentioned if explicitly stated in the transcript?
           n) Are potential needs for transport insurance, staff-related insurances, and cyber risk coverage addressed if mentioned in the transcript?
           o) Are personal insurance needs, especially disability insurance, adequately addressed?


         12. Present your corrected email within <corrected_email> tags.

        Remember, your goal is to create a comprehensive, client-specific email that provides valuable information about each insurance type while maintaining a professional and caring tone, following the provided style guide and accurately reflecting the information from the transcript.
        """

        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are an AI assistant that specializes in correcting and improving insurance advice emails, ensuring they are personalized, relevant, and informative to each specific client."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
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