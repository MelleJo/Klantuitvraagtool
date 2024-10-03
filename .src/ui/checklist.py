import streamlit as st

def recording_checklist():
    with st.expander("📋 Opname Checklist", expanded=False):
        st.markdown("### Bespreek de volgende punten tijdens het gesprek:")

        general_items = [
            "Huidige verzekeringssituatie en recente wijzigingen",
            "Specifieke zorgen of risico's van de klant",
            "Budgetoverwegingen en kostenbesparingen",
            "Toekomstplannen (bedrijfsuitbreiding, verhuizing, etc.)",
            "Branchespecifieke risico's",
            "Persoonlijke verzekeringsbehoeften (indien van toepassing)",
            "Clausules (indien van toepassing)",
            "Risico-adressen (zonder echt adres, maar bijvoorbeeld risico-adres-1, risico-adres-2, etc.)",
            "Hoedanigheid van de klant"
        ]

        insurance_specific_items = {
            "Bedrijfsaansprakelijkheid (AVB)": [
                "Huidige dekking en verzekerd bedrag",
                "'Opzicht' clausule en relevantie voor het bedrijf",
                "Productaansprakelijkheid",
                "ZZP'ers of personeel in dienst"
            ],
            "Rechtsbijstand": [
                "Zakelijke en/of privé dekking",
                "Specifieke juridische risico's in de branche"
            ],
            "Inventaris en Goederen": [
                "Onderscheid tussen inventaris en goederenvoorraad",
                "Recente investeringen of waardeveranderingen",
                "Opslag op andere locaties"
            ],
            "Bedrijfsschade": [
                "Uitkeringstermijn en toereikendheid",
                "Recente omzetontwikkelingen",
                "Afhankelijkheid van specifieke leveranciers of afnemers"
            ],
            "Cyberverzekering": [
                "Digitale risico's en databeveiliging",
                "Gebruik van cloudservices en externe IT-diensten"
            ],
            "Gebouwen": [
                "Eigendom of huur",
                "Recente verbouwingen of uitbreidingen",
                "Duurzaamheidsmaatregelen (zonnepanelen, etc.)"
            ],
            "Wagenpark/Vervoer": [
                "Aantal en type voertuigen",
                "Gebruik van privévoertuigen voor zakelijke doeleinden",
                "Transport van goederen"
            ],
            "Milieuschade": [
                "Opslag van gevaarlijke stoffen",
                "Risico's voor bodem- of waterverontreiniging"
            ],
            "Arbeidsongeschiktheid en Pensioen": [
                "Huidige AOV-dekking en wachttijd",
                "Pensioenvoorzieningen voor ondernemer en personeel"
            ]
        }

        st.markdown("#### Algemene punten:")
        for item in general_items:
            st.checkbox(item, key=f"checklist_general_{item}")

        for category, items in insurance_specific_items.items():
            st.markdown(f"#### {category}:")
            for item in items:
                st.checkbox(item, key=f"checklist_{category}_{item}")

def add_checklist_css():
    st.markdown("""
    <style>
    .streamlit-expanderHeader {
        font-size: 18px;
        color: #1E40AF;
    }
    .stCheckbox {
        padding: 3px 0;
    }
    .stCheckbox label {
        font-size: 14px;
        color: #333;
    }
    .stCheckbox input:checked + label {
        font-weight: bold;
        color: #1E40AF;
    }
    .stExpander {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stExpander > div:first-child {
        border-bottom: 1px solid #E5E7EB;
    }
    .stMarkdown h3 {
        font-size: 16px;
        margin-bottom: 10px;
    }
    .stMarkdown h4 {
        font-size: 14px;
        margin-top: 15px;
        margin-bottom: 5px;
        color: #1E40AF;
    }
    </style>
    """, unsafe_allow_html=True)