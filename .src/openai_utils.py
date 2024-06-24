from openai import OpenAI
import streamlit as st

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("OpenAI API key not found. Please set it in Streamlit Secrets.")
    client = None