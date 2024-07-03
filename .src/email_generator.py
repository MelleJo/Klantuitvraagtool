from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

def generate_email_body(transcript, api_key):
    template = """
    Je bent een Nederlandse e-mail assistent en AI verzekeringsadviseur. Gebruik de volgende transcriptie om een gedetailleerde e-mail in het Nederlands te genereren:

    {transcript}

    Volg deze structuur:
    1. Standaardtekst: Begin met een korte introductie over het belang van up-to-date verzekeringen.
    2. Huidige verzekeringen: Som de actieve verzekeringen en verzekerde bedragen op uit de transcriptie.
    3. Algemene vragen: Stel relevante vragen over de sector of situatie van de klant.
    4. Slimme aanbevelingen: Analyseer de informatie en stel eventuele aanpassingen of extra verzekeringen voor.
    5. Afspraak maken: Voeg een standaardtekst toe over het maken van een afspraak.

    STRIKTE REGELS:
    1. Schrijf UITSLUITEND in het Nederlands.
    2. Begin direct met de inhoud, zonder aanhef.
    3. Eindig zonder groet of ondertekening.
    4. Gebruik een professionele maar vriendelijke toon.
    5. Wees bondig maar informatief.

    BELANGRIJK: 
    - Identificeer het type bedrijf en pas je aanbevelingen daarop aan.
    - Stel voor elke slimme aanbeveling een bevestigingsvraag op voor de adviseur.
    """

    prompt = ChatPromptTemplate.from_template(template)
    
    model = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=api_key)
    
    chain = LLMChain(llm=model, prompt=prompt)

    try:
        result = chain.run(transcript=transcript)
        return result.strip()
    except Exception as e:
        raise Exception(f"Fout bij het genereren van e-mailtekst: {str(e)}")