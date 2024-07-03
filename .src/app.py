import streamlit as st
from openai import OpenAI
import json
from audio_processing import process_audio_input
import pyperclip

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

def analyze_product_info_and_risks(transcript, insurance_products):
    prompt = f"""
    Je bent een AI verzekeringsadviseur. Analyseer de volgende transcriptie en de huidige verzekeringen van de klant:

    Transcriptie: {transcript}

    Huidige verzekeringen: {', '.join(insurance_products)}

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

def main():
    st.set_page_config(page_title="Verzekeringsadviseur E-mail Generator", layout="wide")
    
    st.title("Verzekeringsadviseur E-mail Generator")
    
    if 'transcript' not in st.session_state:
        st.session_state['transcript'] = ""
    if 'email_body' not in st.session_state:
        st.session_state['email_body'] = ""
    if 'product_info' not in st.session_state:
        st.session_state['product_info'] = {}

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Audio Opname of Upload")
        input_method = st.radio("Kies invoermethode", ["Upload audio", "Neem audio op"])
        
        if st.button("Start Transcriptie"):
            st.session_state['transcript'] = process_audio_input(input_method)

        st.subheader("Transcript")
        if st.session_state['transcript']:
            st.session_state['transcript'] = st.text_area("Bewerk transcript indien nodig", value=st.session_state['transcript'], height=200)

        insurance_products = load_insurance_products()
        selected_products = st.multiselect("Selecteer huidige verzekeringen van de klant", insurance_products)

        if st.button("Analyseer en Genereer E-mail"):
            if st.session_state['transcript']:
                with st.spinner("Bezig met analyseren en e-mail genereren..."):
                    st.session_state['product_info'] = analyze_product_info_and_risks(st.session_state['transcript'], selected_products)
                    st.session_state['email_body'] = generate_email_body(st.session_state['transcript'], selected_products)
                st.success("Analyse voltooid en e-mailtekst gegenereerd!")
            else:
                st.warning("Transcribeer eerst de audio of voer handmatig een transcript in.")

    with col2:
        st.subheader("AI Verzekeringsadviseur Analyse")
        if st.session_state['product_info']:
            st.json(st.session_state['product_info'])
            
            st.subheader("Bevestig Bijlage-inhoud")
            recommended_products = st.session_state['product_info'].get('aanbevolen_bijlage_inhoud', [])
            selected_for_attachment = st.multiselect("Selecteer producten voor de bijlage", recommended_products, default=recommended_products)
            
            if st.button("Genereer Bijlage"):
                st.success("Bijlage gegenereerd! (Implementatie vereist)")

        st.subheader("Gegenereerde E-mailtekst")
        if st.session_state['email_body']:
            st.text_area("E-mailtekst", value=st.session_state['email_body'], height=300)
            if st.button("Kopieer naar Klembord"):
                pyperclip.copy(st.session_state['email_body'])
                st.success("E-mailtekst gekopieerd naar klembord!")

if __name__ == "__main__":
    main()