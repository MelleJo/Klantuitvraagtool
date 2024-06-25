from openai_utils import client

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
    
    # Extra controle om er zeker van te zijn dat we alleen de hoofdtekst hebben
    lines = generated_text.split('\n')
    cleaned_lines = [line for line in lines if not line.startswith(('Beste', 'Geachte', 'Met vriendelijke groet', 'Hoogachtend'))]
    cleaned_text = '\n'.join(cleaned_lines)
    
    return cleaned_text