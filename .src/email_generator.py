from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback
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

def generate_email(transcript, email_templates, api_key):
    template = """
    Je bent een Nederlandse e-mail assistent. Gebruik de volgende transcriptie om ALLEEN de hoofdtekst van een e-mail in het Nederlands te genereren:

    {transcript}

    Gebruik de volgende template als inspiratie voor de structuur van je e-mail, maar pas deze aan op basis van de inhoud van de transcriptie:

    Opening: {opening}

    STRIKTE REGELS:
    1. Schrijf UITSLUITEND in het Nederlands.
    2. Begin direct met de inhoud, zonder aanhef.
    3. Eindig zonder groet of ondertekening.
    4. Focus op:
       a. Verwijzing naar het recente gesprek (gebruik hiervoor de 'opening' als inspiratie)
       b. Uitwerking van de hoofdpunten uit de transcriptie
       c. Suggestie voor vervolgstappen
    5. Gebruik een professionele maar vriendelijke toon.

    BELANGRIJK: Genereer ALLEEN de hoofdtekst, niets anders. Gebruik de template alleen als inspiratie voor de toon en structuur, niet voor de exacte bewoording.
    """

    prompt = ChatPromptTemplate.from_template(template)
    
    model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=api_key)
    
    chain = LLMChain(llm=model, prompt=prompt)

    try:
        with get_openai_callback() as cb:
            result = chain.run(transcript=transcript, opening=email_templates['default']['opening'])
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
        
        cleaned_text = clean_text(result)
        
        # Als de tekst nog steeds Engels lijkt, forceer dan een Nederlandse foutmelding
        if not any(dutch_word in cleaned_text.lower() for dutch_word in ['de', 'het', 'een', 'en', 'is']):
            cleaned_text = "Er is een fout opgetreden bij het genereren van de Nederlandse e-mailtekst. Probeer het opnieuw of neem contact op met de systeembeheerder."
        
        print(f"Generated Text (first 100 chars): {cleaned_text[:100]}...")
        return cleaned_text, cb
    except Exception as e:
        print(f"Error in generate_email: {str(e)}")
        raise Exception(f"Fout bij het genereren van e-mailtekst: {str(e)}")