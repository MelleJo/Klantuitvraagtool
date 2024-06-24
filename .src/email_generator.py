from openai_utils import client

def generate_email(transcript, email_templates):
    prompt = f"""
    Gegeven de volgende transcriptie van de notities van een adviseur:
    
    {transcript}
    
    Genereer een professionele e-mail aan de klant op basis van deze informatie. 
    De e-mail moet de volgende structuur volgen:
    
    1. Begroeting
    2. Verwijzing naar het recente gesprek
    3. Hoofdpunten uit de transcriptie, professioneel uitgewerkt
    4. Suggestie voor vervolgstappen of een oproep tot actie
    5. Professionele afsluiting
    
    Gebruik een vriendelijke maar professionele toon in de hele e-mail.
    De e-mail moet in het Nederlands zijn.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "U bent een professionele assistent van een financieel adviseur, belast met het opstellen van e-mails aan klanten op basis van de notities van de adviseur."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content