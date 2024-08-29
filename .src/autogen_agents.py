import autogen
from typing import Dict, Any, List
import streamlit as st
import logging
import json
import os
import streamlit as st
from openai import OpenAI

os.environ["AUTOGEN_USE_DOCKER"] = "0"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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


def generate_email(transcript: str, enhanced_coverage: str, selected_recommendations: str) -> str:
    try:
        enhanced_coverage_list = json.loads(enhanced_coverage)
        selected_recommendations_list = json.loads(selected_recommendations)
        product_descriptions = load_product_descriptions()

        current_coverage = []
        for item in enhanced_coverage_list:
            title = item.get('title', 'Onbekende verzekering').replace('- ', '').strip()
            coverage = item.get('coverage', 'Geen details beschikbaar')
            description = ''

            for category, products in product_descriptions.items():
                if isinstance(products, dict):
                    for product, details in products.items():
                        if product.lower() in title.lower():
                            description = details.get('description', '')
                            break
                    if description:
                        break
                        
            current_coverage.append(f"{title}:\n{coverage}\nOfficiële beschrijving: {description}")

        current_coverage_str = "\n\n".join(current_coverage)

        guidelines = """
        # Verzekeringsadvies E-mail Richtlijnen

        1. Begin met een persoonlijke introductie die de klant bedankt en uitlegt waarom je contact opneemt.
        2. Gebruik een informele, persoonlijke toon (je/jij), tenzij het transcript aangeeft dat formeel taalgebruik (u) nodig is.
        3. Integreer de officiële productbeschrijvingen naadloos in de uitleg van de huidige situatie.
        4. Geef concrete, specifieke adviezen gebaseerd op de situatie van de klant.
        5. Stel bij elk onderwerp een relevante vraag om de klant te betrekken.
        6. Vermijd het noemen van eigen risico's of veronderstellen dat de klant ergens niet voor verzekerd is.
        7. Gebruik korte, krachtige zinnen en paragrafen.
        8. Sluit af met een beknopte, vriendelijke uitnodiging om te reageren.
        9. Vermeld altijd het telefoonnummer 0578-699760.
        10. Maak geen aannames over wanneer verzekeringen voor het laatst zijn gewijzigd.
        11. Gebruik geen termen als "profiteren" bij het beschrijven van verzekeringssituaties.
        12. Geef een korte uitleg over waarom bepaalde wijzigingen of toevoegingen aan de verzekering voordelig kunnen zijn.
        13. Vraag bij elke aanbeveling of de klant een berekening wil ontvangen voor premievergelijking.
        14. Vermeld bij de arbeidsongeschiktheidsverzekering dat dit gebaseerd is op de gegevens bij Veldhuis Advies.
        15. Bij het bespreken van de bedrijfsschadeverzekering, leg uit waarom tegenwoordig de hersteltijd na een calamiteit langer kan duren (bijv. schaarste van materialen en personeel, langere levertijden).
        16. Gebruik een vriendelijke en open toon bij het bespreken van mogelijke personeelswijzigingen, bijvoorbeeld: "Mocht je inmiddels personeel hebben, dan...".
        17. Wanneer je spreekt over mogelijk nieuw personeel, noem ook dat dit nieuwe risico's met zich mee kan brengen die we samen kunnen bespreken.
        18. Vraag bij een AVB (aansprakelijkheidsverzekering), rechtsbijstandsverzekering altijd aan dat het van groot belang is dat het belangrijk of de hoedanigheid (ingesproken door adviseur in transcript, zo niet geef je aan [HOEDANIGHEID]) nog overeen komt. Dat is echt belangrijk.
        19. Als je vraagt om iets te controleren of iets nog correct is: hoedanigheid, kms, waarde, et cetera, dan is het van cruciaal belang dat je ook aangeeft wat er momenteel op de polis staat. Mocht je deze informatie niet uit het transcript kunnen halen dan maak je een placeholder (met []) en geef je aan dat de adviseur dat nog moet invullen. Bovendien is het bij het "controleren" van iets niet een kwestie van "het kan lonen om het aan te passen" maar: als dit veranderd is, dan moet dit worden aangepast op de polis.
        20. Bij personeel, overweeg het volgende (herschrijf uiteraard): (je kunt overwegen om een WIA-excedent (ongevallen)of WGA Hiaat aan te schaffen, het kan prettig zijn voor je personeel, dit kan helpen met het behouden van personeel. Mocht je hier eens over in gesprek willen gaan dan hoor ik het graag.).
        21. Iets als een "brutal loan verzekering" bestaat niet, gebruik alleen bestaande verzekeringen (of onderwerpen), als je iets niet goed kunt plaatsen op basis van het transcript dan zet je gewoon je gedachten/vraag binnen [] als een placeholder dat de adviseur dit zelf nog gaat aanvullen.
        22. Bij een woonhuisverzekering: u heeft een woonhuisverzekering bij ons lopen. De volgende aspecten kunnen van invloed zijn op de dekking: zonnepanelen, zwembad, aanbouw, verbouwing. Mocht er iets veranderd zijn dan horen we het graag.
        23. In plaats van: "Gezien de mogelijke hoge dagwaarde, is het verstandig om te controleren of de dekking nog voldoende is." doe je iets meer in de trant van: "Het kan verstandig om te evalueren wat de huidige dagwaarde is en of de dekking nog steeds gewenst is?".
        24. Indien reisverzekering zonder annulering: Reis je vaak / boek je vaak in het jaar een vakantie, overweeg dan...
        25. Geef nooit aan dat iets "goed" is verzekerd, dat is immers een subjectief oordeel.
        26. Gebruik geen afkortingen die een verzekeringsleek niet begrijpt, zoals SVI.
        27. Indien over een auto of bestelauto, bespreek altijd WA/Casco/beperkt casco, dat bespreek je i.v.m. de dagwaarde en de input van de adviseur.
        28. Noem altijd de clausules en alarmeisen, uiteraard haal je deze informatie enkel uit het transcript en verzin je ze niet.
        29. Zorg heel duidelijk dat je verzekeringen niet met elkaar verwart.
        30. Vraag nooit de klant hoe die een dekking ervaart, dat is waardeloos.
        31. De opzicht clausule (wel of niet) is cruciaal bij het bespreken van de AVB, mocht daar geen info over instaan in het transcript maak dan een placeholder met de boodschap aan de adviseur om dit aan te vullen.
        32. ZZP of personeel (wel of niet) is cruciaal bij het bespreken van de AVB, mocht daar geen info over instaan in het transcript maak dan een placeholder met de boodschap aan de adviseur om dit aan te vullen. Hierbij is het belangrijk aan te geven dat zelfs als iemand je tijdelijk mee helpt, dat je dan geen ZZP'er meer bent voor de verzekering (en uitkering daarvan).
        33. Geef nooit aan dat het "voordelig" kan zijn om een dekking uit te breiden, dat kost immers altijd meer geld.
        34. Er zijn verzekeringen waarbij we veel kunnen vergelijken (auto’s, bestelauto’s, inboedel, avb, bedrijfsschade, brand) en verzekeringen waarbij we niet veel kunnen vergelijken (garage, RB, cyber), wat dus betekent dat we bij de verzekeringen waar we wel kunnen vergelijken aan kunnen bieden om een vergelijk op te stellen. Maar bij een verzekering waarbij we niet veel kunnen vergelijken, dat je dan aangeeft dat we een offerte kunnen maken of het uitzoeken maar niet vergelijken.
        35. Indien inboedel en inventaris (goederen), geef dan altijd het verschil aan tussen goederen en inventaris, met een voorbeeld. Doe hetzelfde met huurdersbelang en eigenaarsbelang.
        36. Geef aan dat i.v.m. vergunningen, personeelstekort en andere omstandigheden het tegenwoordig vaak vrij lang duurt voordat je weer "draait" als onderneming. Dus dat het best verstandig kan zijn om te evalueren of het uitkeringstermijn van de bedrijfsschade wel voldoende is.
        37. Zeg nooit, tenzij expliciet vermeldt, iets over het eigen risico.
        38. In geval van AOV/pensioen noem iets in de trant van het volgende: Als ondernemer kan je pensioen kan je opbouwen via bancaire lijfrente, fiscaal aantrekkelijk om te sparen, nog niet zo bekend onder ondernemers. Heb je daar interesse in en dan kunnen we een afspraak plannen. Het is verstandig om daar een beetje op tijd mee te beginnen. Zouden we je daar een keer over kunnen bellen. 
        """

        email_structure = """
        Schrijf een e-mail met de volgende structuur:

        1. Persoonlijke introductie
        2. Voor elke relevante verzekering in de huidige dekking:
           - Naam verzekering (in bold)
           - Huidige situatie: Beschrijf hier duidelijk en uitgebreid wat de verzekering precies doet. Hier kun je informatie over de verzekeringsproducten vandaan halen: {product_descriptions}, en indien genoemd ook de dekking van de klant als daar bepaalde details in zijn. Hier is het ontzettend belangrijk dat je niet hallucineert of assumpties maakt. Geef ook altijd een duidelijk illustratief voorbeeld.
           - Advies: Geef een concreet advies of aandachtspunt, gebaseerd op de huidige situatie en mogelijke risico's. Leg uit waarom dit advies voordelig kan zijn.
           - Vraag: Stel een relevante vraag om de klant te betrekken, inclusief een aanbod om een berekening te maken voor premievergelijking

        3. Eventuele overige aandachtspunten (bijv. over personeel of specifieke risico's)
        4. Het einde moet zoiets zijn als: ik ga er van uit dat ik je hier mee duidelijkheid geef over je / op weg helpen -> graag hoor ik of alle informatie nog actueel is, en of ik je ergens mee kan helpen?)
        """

        prompt = f"""
        {guidelines}
        {email_structure}
        
        Gebruik de volgende informatie:
        
        Introductie:
        Beste [Naam],
        Ik zie in ons dossier dat u al sinds enige tijd een aantal verzekeringen bij ons hebt lopen. Ik heb mij verdiept in jouw bedrijf en de verzekeringen die je hebt lopen. En daar vallen me een paar dingen in op, die ik graag met je wil bespreken.

        Huidige dekking:
        {current_coverage_str}
        Transcript: {transcript}
        Geselecteerde aanbevelingen: {json.dumps(selected_recommendations_list, ensure_ascii=False)}

        Genereer nu een e-mail volgens bovenstaande richtlijnen en structuur. Zorg ervoor dat de e-mail volledig is en alle gevraagde elementen bevat, inclusief de introductie, officiële productbeschrijvingen, en de specifieke punten over de bedrijfsschadeverzekering en mogelijke personeelswijzigingen.
        """

        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Je bent een ervaren verzekeringsadviseur bij Veldhuis Advies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )

        email_content = response.choices[0].message.content.strip()
        
        if not email_content:
            raise ValueError("Email generation returned empty content.")

        logging.info("Email generated successfully")
        logging.debug(f"Email content: {email_content[:500]}...")  # Log first 500 chars

        return email_content

    except Exception as e:
        logging.error(f"Error in generate_email: {str(e)}")
        logging.error(f"Error type: {type(e)}")
        logging.error(f"Error args: {e.args}")
        logging.error(f"Transcript: {transcript}")
        logging.error(f"Enhanced coverage: {enhanced_coverage}")
        logging.error(f"Selected recommendations: {selected_recommendations}")
        raise


def correction_AI(guidelines: str, email_content: str) -> str:
    # Construct the prompt for the correction AI
    prompt = f"""
    You check line by line the {email_content} and check if it adheres to {guidelines}, if you see it is somewhere not adhering you fix that.
    """

    # Call the GPT-4o model to correct the email
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an assistant that specializes in correcting AI-generated content based on strict guidelines."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,  # Adjust based on expected output length
        temperature=0.2  # Low temperature for deterministic output
    )

    # Extract the corrected email content
    corrected_email = response['choices'][0]['message']['content'].strip()

    return corrected_email 


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