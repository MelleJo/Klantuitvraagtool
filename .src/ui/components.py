import streamlit as st
from typing import List, Any
import json

def ImprovedUIStyled():
    st.markdown(
        """
        <style>
          body {
            font-family: 'Roboto', sans-serif;
            background-color: #f0f4f8;
            color: #333;
          }

          .stApp {
            background-color: #ffffff;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
          }

          h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif;
            color: #1e3a8a;
          }

          .stButton > button {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: background-color 0.3s ease;
          }

          .stButton > button:hover {
            background-color: #2563eb;
          }

          .stTextInput > div > div > input,
          .stTextArea > div > div > textarea {
            border: 1px solid #d1d5db;
            border-radius: 5px;
            padding: 0.5rem;
          }

          .step-container {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
          }

          .metric-container {
            background-color: #dbeafe;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
          }

          .stExpander {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 1rem;
          }

          .stExpander > div:first-child {
            background-color: #f3f4f6;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
          }

          .recommendation-card {
            background-color: #fff;
            border: 1px solid #e5e7eb;
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
            color: #1e3a8a;
            margin-bottom: 0.5rem;
          }

          .recommendation-content {
            font-size: 0.9rem;
            color: #4b5563;
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
            color: #3b82f6;
            font-weight: bold;
          }

          .stProgress > div > div > div > div {
            background-color: #3b82f6;
          }
        </style>
        """,
        unsafe_allow_html=True
    )

def display_input_method_selector(input_methods: List[str]) -> str:
    """Display a selector for input methods."""
    return st.selectbox("Selecteer invoermethode:", input_methods, key="input_method_selector")

def display_text_input() -> str:
    """Display a text input area."""
    return st.text_area("Voer tekst in of plak tekst:", height=200, key="text_input")

def display_file_uploader(allowed_types: List[str]) -> Any:
    """Display a file uploader."""
    return st.file_uploader("Upload een bestand:", type=allowed_types, key="file_uploader")

def display_generate_button(label: str = "Genereer") -> bool:
    """Display a generate button."""
    return st.button(label, key=f"generate_button_{label}")

def display_progress_bar(progress: float) -> None:
    """Display a progress bar."""
    st.progress(progress, key="progress_bar")

def display_spinner(text: str) -> Any:
    """Display a spinner with custom text."""
    return st.spinner(text)

def display_success(message: str) -> None:
    """Display a success message."""
    st.success(message)

def display_error(message: str) -> None:
    """Display an error message."""
    st.error(message)

def display_warning(message: str) -> None:
    """Display a warning message."""
    st.warning(message)

def display_metric(label: str, value: Any) -> None:
    """Display a metric with a label and value."""
    st.markdown(f"""
    <div class="metric-container">
        <p style='font-size: 14px; color: #555; margin-bottom: 5px;'>{label}</p>
        <p style='font-size: 20px; font-weight: bold; margin: 0;'>{value}</p>
    </div>
    """, unsafe_allow_html=True)