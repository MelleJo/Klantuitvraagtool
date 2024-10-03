import streamlit as st

def recording_checklist():
    with st.expander("📋 Opname Checklist", expanded=False):
        st.markdown("### Bespreek de volgende punten tijdens het gesprek:")

        checklist_items = [
            "Huidige verzekeringen en dekkingen",
            "Recente wijzigingen in bedrijfs- of persoonlijke situatie",
            "Specifieke zorgen of risico's",
            "Budgetoverwegingen",
            "Plannen voor bedrijfsuitbreiding of veranderingen",
            "Personeelsgerelateerde verzekeringsbehoeften",
            "Updates over eigendommen en bezittingen",
            "Cyberveiligheidszorgen",
            "Branchespecifieke risico's",
            "Persoonlijke verzekeringsbehoeften (indien van toepassing)",
            "Bedrijfsaansprakelijkheid en 'opzicht' clausule",
            "Inventaris vs. goederenvoorraad",
            "Bedrijfsschadeverzekering en uitkeringstermijn",
            "Waardebepaling van bedrijfsmiddelen",
            "Transportrisico's",
            "Milieuschaderisico's",
            "Machinebreuk en bedrijfsstilstand"
        ]

        for item in checklist_items:
            st.checkbox(item, key=f"checklist_{item}")

        

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
    </style>
    """, unsafe_allow_html=True)