import streamlit as st

def apply_custom_css():
    """Apply custom CSS to improve the app's appearance and user experience."""
    st.markdown("""
        <style>
        .main {
            background-color: #f0f2f6;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .step-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .metric-container {
            background-color: #e1e8ed;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .stTextInput > div > div > input {
            background-color: #f9f9f9;
        }
        .stTextArea > div > div > textarea {
            background-color: #f9f9f9;
        }
        .step {
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            background-color: #e0e0e0;
            color: #333;
        }
        .step.active {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .step.completed {
            background-color: #81C784;
            color: white;
            text-decoration: line-through;
        }
        .stExpander {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .stExpander > div:first-child {
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            background-color: #f0f0f0;
        }
        .stExpander > div:last-child {
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 5px;
            background-color: white;
        }
        .recommendation-card {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        .recommendation-card:hover {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .recommendation-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .recommendation-content {
            margin-top: 10px;
        }
        .recommendation-list {
            list-style-type: none;
            padding-left: 0;
        }
        .recommendation-list li {
            margin-bottom: 5px;
            padding-left: 20px;
            position: relative;
        }
        .recommendation-list li:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True)