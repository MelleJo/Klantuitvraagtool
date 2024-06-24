from openai_utils import client

def generate_email(transcript, email_templates):
    prompt = f"""
    Gegeven de volgende transcriptie van de notities van een adviseur:
    
    {transcript}
    
    Genereer alleen de hoofdtekst van een professionele e-mail in het Nederlands, gericht aan de klant en gebaseerd op deze informatie. 
    De tekst moet de volgende elementen bevatten:
    
    1. Verwijzing naar het recente gesprek
    2. Hoofdpunten uit de transcriptie, professioneel uitgewerkt
    3. Suggestie voor vervolgstappen of een oproep tot actie
    
    Gebruik een vriendelijke maar professionele toon in de hele tekst.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "U bent een professionele assistent van een financieel adviseur, belast met het opstellen van e-mails aan klanten op basis van de notities van de adviseur."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content