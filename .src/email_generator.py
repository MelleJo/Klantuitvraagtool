from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import StrOutputParser
import re

def clean_text(text):
    # Verwijder e-mail headers
    text = re.sub(r'^(Subject|From|To|Cc|Bcc):.*\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Verwijder aanhef en afsluiting
    text = re.sub(r'^(Dear|Beste|Geachte).*\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n(Sincerely|Best regards|Met vriendelijke groet|Hoogachtend).*$', '', text, flags=re.IGNORECASE)
    
    # Verwijder ondertekening
    text = re.sub(r'\n.*\[Your Name\].*$', '', text, flags=re.MULTILINE | re.DOTALL)
    
    # Verwijder lege regels aan het begin en einde
    text = text.strip()
    
    return text

def generate_email(transcript, api_key):
    template = """
    Gebruik de volgende transcriptie om ALLEEN de hoofdtekst van een e-mail in het Nederlands te genereren:

    {transcript}

    STRIKTE REGELS:
    1. Schrijf UITSLUITEND in het Nederlands.
    2. Begin direct met de inhoud, zonder aanhef.
    3. Eindig zonder groet of ondertekening.
    4. Focus op:
       a. Verwijzing naar het recente gesprek
       b. Uitwerking van de hoofdpunten
       c. Suggestie voor vervolgstappen
    5. Gebruik een professionele maar vriendelijke toon.

    BELANGRIJK: Genereer ALLEEN de hoofdtekst, niets anders.
    """

    prompt = ChatPromptTemplate.from_template(template)
    
    model = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=api_key)
    
    chain = LLMChain(llm=model, prompt=prompt, output_parser=StrOutputParser())

    try:
        result = chain.invoke({"transcript": transcript})
        cleaned_text = clean_text(result['text'])
        
        # Als de tekst nog steeds Engels lijkt, forceer dan een Nederlandse foutmelding
        if not any(dutch_word in cleaned_text.lower() for dutch_word in ['de', 'het', 'een', 'en', 'is']):
            cleaned_text = "Er is een fout opgetreden bij het genereren van de Nederlandse e-mailtekst. Probeer het opnieuw of neem contact op met de systeembeheerder."
        
        return cleaned_text
    except Exception as e:
        raise Exception(f"Fout bij het genereren van e-mailtekst: {str(e)}")