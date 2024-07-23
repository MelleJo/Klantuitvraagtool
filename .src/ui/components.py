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
          @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
          
          body {
            font-family: 'Roboto', sans-serif;
            background-color: #F3F4F6;
            color: #1F2937;
          }

          .stApp {
            background-color: #FFFFFF;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
          }

          h1, h2, h3, h4, h5, h6 {
            font-family: 'Roboto', sans-serif;
            color: #1E40AF;
          }

          .stButton > button {
            background-color: #3B82F6;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: background-color 0.3s ease;
          }

          .stButton > button:hover {
            background-color: #2563EB;
          }

          .stTextInput > div > div > input,
          .stTextArea > div > div > textarea,
          .stSelectbox > div > div > select {
            border: 1px solid #D1D5DB;
            border-radius: 5px;
            padding: 0.5rem;
            background-color: #F9FAFB;
          }

          .step-container {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
          }

          .metric-container {
            background-color: #EFF6FF;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #BFDBFE;
          }

          .stExpander {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
          }

          .stExpander > div:first-child {
            background-color: #F3F4F6;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border-bottom: 1px solid #E5E7EB;
          }

          .recommendation-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: box-shadow 0.3s ease;
          }

          .recommendation-card:hover {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          }

          .recommendation-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1E40AF;
            margin-bottom: 0.5rem;
          }

          .recommendation-content {
            font-size: 0.9rem;
            color: #4B5563;
          }

          .recommendation-list {
            list-style-type: none;
            padding-left: 0;
          }

          .recommendation-list li {
            margin-bottom: 0.5rem;
            padding-left: 1.5rem;
            position: relative;
          }

          .recommendation-list li:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #3B82F6;
            font-weight: bold;
          }

          .stProgress > div > div > div > div {
            background-color: #3B82F6;
          }
        </style>
        """,
        unsafe_allow_html=True
    )