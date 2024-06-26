from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

def generate_email_body(transcript, api_key):
    template = """
    Je bent een Nederlandse e-mail assistent. Gebruik de volgende transcriptie om de hoofdtekst van een e-mail in het Nederlands te genereren:

    {transcript}

    STRIKTE REGELS:
    1. Schrijf UITSLUITEND in het Nederlands.
    2. Begin direct met de inhoud, zonder aanhef.
    3. Eindig zonder groet of ondertekening.
    4. Focus op:
       a. Hoofdpunten uit de transcriptie
       b. Suggestie voor vervolgstappen (indien van toepassing)
    5. Gebruik een professionele maar vriendelijke toon.
    6. Houd de tekst bondig en to-the-point.

    BELANGRIJK: Genereer ALLEEN de hoofdtekst die in Outlook geplakt kan worden.
    """

    prompt = ChatPromptTemplate.from_template(template)
    
    model = ChatOpenAI(model="gpt-4o", temperature=0.7, openai_api_key=api_key)
    
    chain = LLMChain(llm=model, prompt=prompt)

    try:
        result = chain.run(transcript=transcript)
        return result.strip()
    except Exception as e:
        raise Exception(f"Fout bij het genereren van e-mailtekst: {str(e)}")