import autogen
from typing import Dict, Any
import streamlit as st
import logging
import json
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI config
config_list = [
    {
        'model': 'gpt-4o-2024-08-06',
        'api_key': st.secrets["OPENAI_API_KEY"]
    }
]

# Define agents
user_proxy = autogen.UserProxyAgent(
    name="User",
    system_message="A human user interacting with the insurance advisor system.",
    code_execution_config=False
)

transcript_analyst = autogen.AssistantAgent(
    name="TranscriptAnalyst",
    system_message="You are an expert in analyzing insurance-related transcripts. Your role is to extract key information about the client's current insurance coverage and potential needs.",
    llm_config={"config_list": config_list}
)

recommendation_agent = autogen.AssistantAgent(
    name="RecommendationAgent",
    system_message="You are an expert in insurance products and generating tailored recommendations. Your role is to suggest appropriate insurance products based on the client's needs and current coverage.",
    llm_config={"config_list": config_list}
)

email_generator = autogen.AssistantAgent(
    name="EmailGenerator",
    system_message="You are an expert in crafting personalized and professional emails. Your role is to create a client-friendly email summarizing the insurance analysis and recommendations.",
    llm_config={"config_list": config_list}
)

quality_control = autogen.AssistantAgent(
    name="QualityControl",
    system_message="You are responsible for reviewing and improving the outputs from other agents. Ensure all content is accurate, professional, and tailored to the client's needs.",
    llm_config={"config_list": config_list}
)

def analyze_transcript(transcript: str) -> Dict[str, Any]:
    try:
        logger.info("Starting transcript analysis")
        user_proxy.initiate_chat(
            transcript_analyst,
            message=f"Please analyze this insurance-related transcript and extract key information about the client's current coverage and potential needs:\n\n{transcript}"
        )
        
        analysis = transcript_analyst.last_message()["content"]
        logger.info("Transcript analysis completed")
        
        user_proxy.initiate_chat(
            recommendation_agent,
            message=f"Based on this analysis, please generate tailored insurance recommendations:\n\n{analysis}"
        )
        
        recommendations = recommendation_agent.last_message()["content"]
        logger.info("Recommendations generated")
        
        return {
            "analysis": analysis,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Error in analyze_transcript: {str(e)}", exc_info=True)
        return {"error": str(e)}

def generate_email(transcript: str, analysis: str, recommendations: str) -> str:
    try:
        logger.info("Starting email generation")
        user_proxy.initiate_chat(
            email_generator,
            message=f"Please generate a personalized email for the client based on this transcript, analysis, and recommendations:\n\nTranscript: {transcript}\n\nAnalysis: {analysis}\n\nRecommendations: {recommendations}"
        )
        
        email_draft = email_generator.last_message()["content"]
        logger.info("Email draft generated")
        
        user_proxy.initiate_chat(
            quality_control,
            message=f"Please review and improve this email draft:\n\n{email_draft}"
        )
        
        final_email = quality_control.last_message()["content"]
        logger.info("Final email generated")
        
        return final_email
    except Exception as e:
        logger.error(f"Error in generate_email: {str(e)}", exc_info=True)
        raise

def load_insurance_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'insurance_advisor_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Insurance advisor prompt file not found at {prompt_path}")
        return ""

def initialize_agents():
    insurance_prompt = load_insurance_prompt()
    transcript_analyst.update_system_message(insurance_prompt)
    logger.info("Agents initialized with insurance advisor prompt")

# Initialize agents when this module is imported
initialize_agents()