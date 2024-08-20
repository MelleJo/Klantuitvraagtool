import streamlit as st
from typing import List, Any

def display_input_method_selector(input_methods: List[str]) -> str:
    return st.selectbox("Selecteer invoermethode:", input_methods, key="input_method_selector")

def display_text_input() -> str:
    return st.text_area("Voer tekst in of plak tekst:", height=200, key="text_input")

def display_file_uploader(allowed_types: List[str]) -> Any:
    return st.file_uploader("Upload een bestand:", type=allowed_types, key="file_uploader")

def display_generate_button(label: str = "Genereer") -> bool:
    return st.button(label, key=f"generate_button_{label}")

def display_progress_bar(progress: float) -> None:
    st.progress(progress, key="progress_bar")

def display_spinner(text: str) -> Any:
    return st.spinner(text)

def display_success(message: str) -> None:
    st.success(message)

def display_error(message: str) -> None:
    st.error(message)

def display_warning(message: str) -> None:
    st.warning(message)

def display_metric(label: str, value: Any) -> None:
    st.markdown(f"""
    <div class="metric-container">
        <p style='font-size: 14px; color: #555; margin-bottom: 5px;'>{label}</p>
        <p style='font-size: 20px; font-weight: bold; margin: 0;'>{value}</p>
    </div>
    """, unsafe_allow_html=True)

def ImprovedUIStyled():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        :root {
            --primary-color: #3B82F6;
            --secondary-color: #1E40AF;
            --background-color: #F3F4F6;
            --text-color: #1F2937;
            --accent-color: #10B981;
            --error-color: #EF4444;
            --warning-color: #F59E0B;
            --success-color: #10B981;
        }
        
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }

        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--secondary-color);
            font-weight: 500;
            margin-bottom: 1rem;
        }

        h1 {
            font-size: 2.5rem;
        }

        h2 {
            font-size: 2rem;
        }

        h3 {
            font-size: 1.75rem;
        }

        p {
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: background-color 0.3s ease, transform 0.1s ease;
        }

        .stButton > button:hover {
            background-color: var(--secondary-color);
            transform: translateY(-1px);
        }

        .stButton > button:active {
            transform: translateY(1px);
        }

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            border: 1px solid #D1D5DB;
            border-radius: 5px;
            padding: 0.5rem;
            background-color: #F9FAFB;
            transition: border-color 0.3s ease;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }

        .step-container {
            background-color: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: box-shadow 0.3s ease;
        }

        .step-container:hover {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .recommendation-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: box-shadow 0.3s ease, transform 0.3s ease;
        }

        .recommendation-card:hover {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }

        .stProgress > div > div > div > div {
            background-color: var(--primary-color);
        }

        .stAlert {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }

        .stAlert.success {
            background-color: #D1FAE5;
            color: #065F46;
            border: 1px solid #34D399;
        }

        .stAlert.error {
            background-color: #FEE2E2;
            color: #991B1B;
            border: 1px solid #F87171;
        }

        .stAlert.warning {
            background-color: #FEF3C7;
            color: #92400E;
            border: 1px solid #FBBF24;
        }

        .stAlert.info {
            background-color: #DBEAFE;
            color: #1E40AF;
            border: 1px solid #60A5FA;
        }

        .stExpander {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 1rem;
        }

        .stExpander > div:first-child {
            background-color: #F3F4F6;
            padding: 0.75rem 1rem;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .stExpander > div:first-child:hover {
            background-color: #E5E7EB;
        }

        .stExpander > div:last-child {
            padding: 1rem;
        }

        .metric-container {
            background-color: #F3F4F6;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #E5E7EB;
        }

        .metric-container h4 {
            margin-bottom: 0.5rem;
            color: var(--secondary-color);
        }

        .metric-container p {
            font-size: 1.25rem;
            font-weight: 500;
            color: var(--text-color);
        }

        /* Custom styling for file uploader */
        .stFileUploader > div > button {
            background-color: var(--primary-color);
            color: white;
        }

        .stFileUploader > div > button:hover {
            background-color: var(--secondary-color);
        }

        /* Custom styling for checkbox */
        .stCheckbox > label > div[role="checkbox"] {
            border-color: var(--primary-color);
        }

        .stCheckbox > label > div[role="checkbox"]::before {
            background-color: var(--primary-color);
        }

        /* Custom styling for radio buttons */
        .stRadio > label > div[role="radio"] {
            border-color: var(--primary-color);
        }

        .stRadio > label > div[role="radio"]::before {
            background-color: var(--primary-color);
        }

        /* Responsive design adjustments */
        @media (max-width: 768px) {
            .stApp {
                padding: 1rem;
            }

            h1 {
                font-size: 2rem;
            }

            h2 {
                font-size: 1.75rem;
            }

            h3 {
                font-size: 1.5rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )