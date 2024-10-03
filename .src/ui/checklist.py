import streamlit as st

def add_checklist_css():
    st.markdown("""
    <style>
    .stCheckbox {
        padding: 5px 0;
    }
    .stCheckbox label {
        font-size: 14px;
        color: #333;
    }
    .stCheckbox input:checked + label {
        font-weight: bold;
        color: #1E40AF;
    }
    .sidebar .stMarkdown h2 {
        color: #1E40AF;
        font-size: 18px;
        margin-bottom: 10px;
    }
    .sidebar .stMarkdown hr {
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def recording_checklist():
    st.sidebar.markdown("## 📋 Recording Checklist")
    st.sidebar.markdown("Ensure you cover these points during the conversation:")

    checklist_items = [
        "Current insurance policies",
        "Recent changes in business or personal situation",
        "Specific concerns or risks",
        "Budget considerations",
        "Plans for business expansion or changes",
        "Employee-related insurance needs",
        "Property and asset updates",
        "Cyber security concerns",
        "Industry-specific risks",
        "Personal insurance needs (if applicable)"
    ]

    for item in checklist_items:
        st.sidebar.checkbox(item, key=f"checklist_{item}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("Remember to ask open-ended questions and listen carefully to the client's responses.")