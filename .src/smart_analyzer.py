from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

def analyze_product_info_and_risks(transcript, api_key):
    template = """
    Je bent een AI verzekeringsadviseur. Analyseer de volgende transcriptie en identificeer de relevante producten en risico's:

    {transcript}

    Volg deze stappen:
    1. Identificeer alle genoemde verzekeringsproducten.
    2. Voor elk product, beschrijf kort de belangrijkste dekking en risico's.
    3. Identificeer eventuele ontbrekende cruciale verzekeringen voor het type bedrijf.
    4. Stel een lijst op van productinformatie en risico's die in de bijlage moeten worden opgenomen.

    Geef je antwoord in het volgende format:
    Geïdentificeerde producten: [lijst van producten]
    Aanbevolen bijlage-inhoud: [lijst van producten en risico's voor de bijlage]
    Ontbrekende cruciale verzekeringen: [lijst van ontbrekende verzekeringen]
    """

    prompt = ChatPromptTemplate.from_template(template)
    
    model = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=api_key)
    
    chain = LLMChain(llm=model, prompt=prompt)

    try:
        result = chain.run(transcript=transcript)
        return result.strip()
    except Exception as e:
        raise Exception(f"Fout bij het analyseren van productinformatie en risico's: {str(e)}")