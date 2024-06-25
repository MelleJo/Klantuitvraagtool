from openai_utils import client

def generate_email(transcript, email_templates):
    prompt = f"""
    Gegeven de volgende transcriptie van de notities van een adviseur:

    {transcript}

    Genereer ALLEEN de hoofdtekst van een professionele e-mail in het Nederlands, gericht aan de klant en gebaseerd op deze informatie. 
    Volg deze strikte regels:

    1. Schrijf UITSLUITEND in het Nederlands.
    2. Produceer ALLEEN de hoofdtekst van de e-mail, zonder aanhef of afsluiting.
    3. Begin direct met de inhoud, zonder 'Beste' of iets dergelijks.
    4. Eindig zonder groet of ondertekening.
    5. Verwijs naar het recente gesprek.
    6. Werk de hoofdpunten uit de transcriptie professioneel uit.
    7. Suggereer vervolgstappen of doe een oproep tot actie.

    Gebruik een vriendelijke maar professionele toon.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",  # Ensure this matches the model name for GPT-4 in your OpenAI account
        messages=[
            {"role": "system", "content": "U bent een Nederlandse assistent die alleen de hoofdtekst van e-mails schrijft, strikt in het Nederlands, zonder aanhef of afsluiting."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content