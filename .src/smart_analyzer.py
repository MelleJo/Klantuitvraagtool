from langchain_community import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import json

def analyze_product_info_and_risks(transcript, api_key):
    template = """
    Je bent een AI verzekeringsadviseur. Analyseer de volgende transcriptie:

    Transcriptie: {transcript}

    Geef je antwoord in het volgende JSON-formaat:
    {{
        "geidentificeerde_producten": ["lijst van producten genoemd in de transcriptie"],
        "aanbevolen_bijlage_inhoud": ["lijst van producten en risico's voor de bijlage"],
        "ontbrekende_cruciale_verzekeringen": ["lijst van ontbrekende verzekeringen"],
        "risico_analyse": "Korte analyse van de belangrijkste risico's voor dit type bedrijf"
    }}
    """

    prompt = ChatPromptTemplate.from_template(template)
    
    model = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=api_key)
    
    chain = LLMChain(llm=model, prompt=prompt)

    try:
        result = chain.run(transcript=transcript)
        return json.loads(result.strip())
    except Exception as e:
        raise Exception(f"Fout bij het analyseren van productinformatie en risico's: {str(e)}")