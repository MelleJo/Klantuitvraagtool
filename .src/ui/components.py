import streamlit as st
from streamlit.components.v1 import html

def ImprovedUIStyled():
    return html(
        """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/react/17.0.2/umd/react.production.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/17.0.2/umd/react-dom.production.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/styled-components/5.3.3/styled-components.min.js"></script>
        <div id="react-root"></div>
        <script>
        const {styled, createGlobalStyle} = styled;
        
        const GlobalStyle = createGlobalStyle`
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
        `;

        const App = () => {
          return React.createElement(React.Fragment, null,
            React.createElement(GlobalStyle, null),
            React.createElement('div', null, 'Styled content goes here')
          );
        };

        ReactDOM.render(
          React.createElement(App, null),
          document.getElementById('react-root')
        );
        </script>
        """
    )