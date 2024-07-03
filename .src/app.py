import streamlit as st
from openai import OpenAI
import json
from audio_processing import process_audio_input
import pyperclip
from docx import Document
from io import BytesIO

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_insurance_products():
    # In a real application, this would load from a database or file
    return [
        "Aansprakelijkheidsverzekering",
        "Bedrijfsschadeverzekering",
        "Cyberverzekering",
        "Rechtsbijstandverzekering",
        "Bestuurdersaansprakelijkheidsverzekering"
    ]

def generate_email_body(transcript, insurance_products):
    prompt = f"""
    Je bent een Nederlandse e-mail assistent voor een verzekeringsadviseur. Gebruik de volgende transcriptie om een e-mail op te stellen:

    {transcript}

    Huidige verzekeringen van de klant: {', '.join(insurance_products)}

    Volg deze structuur:
    1. Standaardtekst: Begin met een korte introductie over het belang van up-to-date verzekeringen.
    2. Huidige verzekeringen: Bevestig de actieve verzekeringen en verzekerde bedragen uit de transcriptie.
    3. Algemene vragen: Stel relevante vragen over de sector of situatie van de klant.
    4. Slimme aanbevelingen: Analyseer de informatie en stel eventuele aanpassingen of extra verzekeringen voor.
    5. Afspraak maken: Voeg een standaardtekst toe over het maken van een afspraak.

    STRIKTE REGELS:
    1. Schrijf UITSLUITEND in het Nederlands.
    2. Begin met een aanhef "Beste [Klantnaam]," (vul geen echte naam in).
    3. Eindig met een groet "Met vriendelijke groet, [Naam Adviseur]" (vul geen echte naam in).
    4. Gebruik een professionele maar vriendelijke toon.
    5. Wees bondig maar informatief.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

def analyze_product_info_and_risks(transcript):
    prompt = f"""
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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)

def create_docx_attachment(products):
    doc = Document()
    doc.add_heading('Productinformatie en Risico\'s', 0)
    
    for product in products:
        doc.add_heading(product, level=1)
        doc.add_paragraph('Hier komt gedetailleerde informatie over het product en de bijbehorende risico\'s.')
        doc.add_paragraph('Deze informatie zou in een echte applicatie uit een database of API worden gehaald.')
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def main():
    st.set_page_config(page_title="Verzekeringsadviseur E-mail Generator", layout="wide")
    
    st.title("Verzekeringsadviseur E-mail Generator")
    
    if 'transcript' not in st.session_state:
        st.session_state['transcript'] = ""
    if 'email_body' not in st.session_state:
        st.session_state['email_body'] = ""
    if 'product_info' not in st.session_state:
        st.session_state['product_info'] = {}

    # Step 1: Record info
    st.subheader("1. Neem audio op")
    new_transcript = process_audio_input()
    if new_transcript:
        st.session_state['transcript'] = new_transcript

    # Step 2 & 3: See and edit transcript
    st.subheader("2. Bekijk en bewerk het transcript")
    if st.session_state['transcript']:
        st.session_state['transcript'] = st.text_area("Bewerk transcript indien nodig", value=st.session_state['transcript'], height=200)
        
        # Step 4: Get AI suggestions
        if st.button("Analyseer Transcript"):
            with st.spinner("Bezig met analyseren..."):
                st.session_state['product_info'] = analyze_product_info_and_risks(st.session_state['transcript'])
            st.success("Analyse voltooid!")

    # Step 5: Choose products
    if st.session_state['product_info']:
        st.subheader("3. Kies producten voor de bijlage")
        st.json(st.session_state['product_info'])
        
        recommended_products = st.session_state['product_info'].get('aanbevolen_bijlage_inhoud', [])
        all_products = load_insurance_products()
        default_selection = list(set(recommended_products) & set(all_products))
        
        selected_products = st.multiselect(
            "Selecteer producten voor de bijlage",
            options=all_products,
            default=default_selection
        )
        
        custom_product = st.text_input("Voeg een eigen product toe")
        if custom_product:
            selected_products.append(custom_product)

        # Step 6: Generate email and attachment
        if st.button("Genereer E-mail en Bijlage"):
            with st.spinner("Bezig met genereren van e-mail en bijlage..."):
                st.session_state['email_body'] = generate_email_body(st.session_state['transcript'], selected_products)
                attachment = create_docx_attachment(selected_products)
            
            st.subheader("4. Gegenereerde E-mailtekst")
            st.text_area("E-mailtekst", value=st.session_state['email_body'], height=300)
            
            if st.button("Kopieer naar Klembord"):
                pyperclip.copy(st.session_state['email_body'])
                st.success("E-mailtekst gekopieerd naar klembord!")
            
            st.download_button(
                label="Download Bijlage",
                data=attachment,
                file_name="productinformatie.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main()