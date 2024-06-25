from openai_utils import client
import re

def generate_email(transcript, email_templates):
    prompt = f"""
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
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "U bent een Nederlandse e-mail assistent die uitsluitend de hoofdtekst van e-mails produceert in het Nederlands, zonder enige opmaak."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    generated_text = response.choices[0].message.content
    
    # Post-processing om ervoor te zorgen dat we alleen Nederlandse inhoud hebben
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
    
    cleaned_text = clean_text(generated_text)
    
    # Als de tekst nog steeds Engels lijkt, forceer dan een Nederlandse foutmelding
    if not any(dutch_word in cleaned_text.lower() for dutch_word in ['de', 'het', 'een', 'en', 'is']):
        cleaned_text = "Er is een fout opgetreden bij het genereren van de Nederlandse e-mailtekst. Probeer het opnieuw of neem contact op met de systeembeheerder."
    
    return cleaned_text