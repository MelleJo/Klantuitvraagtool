import json
import logging
import os
from typing import List, Dict, Any
import streamlit as st
import sys
from pathlib import Path
from autogen_agents import email_generator, quality_control, user_proxy, analyze_transcript as autogen_analyze_transcript
from config import (
    LOG_FILE, LOG_LEVEL, PRODUCT_DESCRIPTIONS_FILE,
    INPUT_METHODS, load_config, OPENAI_MODEL, OPENAI_TEMPERATURE
)

logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

def load_product_descriptions() -> Dict[str, Any]:
    try:
        with open(PRODUCT_DESCRIPTIONS_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"Successfully loaded product descriptions from {PRODUCT_DESCRIPTIONS_FILE}")
        return data
    except FileNotFoundError:
        logger.error(f"The file '{PRODUCT_DESCRIPTIONS_FILE}' was not found.")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in '{PRODUCT_DESCRIPTIONS_FILE}': {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error while loading '{PRODUCT_DESCRIPTIONS_FILE}': {str(e)}")
        return {}

def get_product_description(product_name: str, product_descriptions: Dict[str, Any]) -> str:
    for category, products in product_descriptions.items():
        if isinstance(products, dict) and product_name.lower() in products:
            return products[product_name.lower()].get('description', "Geen beschrijving beschikbaar.")
    return "Geen specifieke productbeschrijving beschikbaar."

def analyze_transcript(transcript: str) -> Dict[str, Any]:
    try:
        logger.info("Starting transcript analysis using AutoGen")
        result = autogen_analyze_transcript(transcript)
        logger.info("Transcript analysis completed")
        return result
    except Exception as e:
        logger.error(f"Error in analyze_transcript: {str(e)}", exc_info=True)
        return {"error": str(e)}


def generate_email(transcript: str, enhanced_coverage: List[Dict[str, str]], selected_recommendations: List[Dict[str, Any]]) -> str:
    try:
        logger.info("Starting email generation using AutoGen")

        analysis = json.dumps(enhanced_coverage, ensure_ascii=False)
        recommendations = json.dumps(selected_recommendations, ensure_ascii=False)

        logger.debug(f"Transcript: {transcript}")
        logger.debug(f"Analysis JSON: {analysis}")
        logger.debug(f"Recommendations JSON: {recommendations}")

        if not transcript or not analysis or not recommendations:
            logger.error("One or more inputs are empty, skipping email generation.")
            raise ValueError("Input data missing or incomplete")

        # Attempt to generate email with markdown formatting
        user_proxy.initiate_chat(
            email_generator,
            message=f"Generate a personalized email for the client based on this transcript, analysis, and recommendations. Use markdown formatting for the email content:\n\nTranscript: {transcript}\n\nAnalysis: {analysis}\n\nRecommendations: {recommendations}"
        )

        initial_email = email_generator.last_message().get("content", "")
        logger.info("Initial email draft generated")
        logger.debug(f"Initial Email: {initial_email[:200]}...")  # Log the first 200 characters for context

        # Check if markdown processing failed and fallback to plain text
        if 'exitcode: 1' in initial_email or 'unknown language markdown' in initial_email:
            logger.warning("Markdown processing failed, attempting plain text fallback")
            user_proxy.initiate_chat(
                email_generator,
                message="The markdown formatting failed. Please generate the email in plain text format."
            )
            initial_email = email_generator.last_message().get("content", "")
            logger.info("Fallback to plain text email draft generated")
            logger.debug(f"Plain Text Email: {initial_email[:200]}...")  # Log the first 200 characters for context

        if not initial_email.strip():
            logger.error("Email generator returned empty content after fallback.")
            raise ValueError("Email generator did not return any content.")

        return initial_email
    except Exception as e:
        logger.error(f"Error in generate_email: {str(e)}", exc_info=True)
        raise







def couple_coverage_with_descriptions(current_coverage: List[str], product_descriptions: Dict[str, Any]) -> List[Dict[str, str]]:
    enhanced_coverage = []
    for item in current_coverage:
        for category, products in product_descriptions.items():
            if isinstance(products, dict):
                for product, details in products.items():
                    if product.lower() in item.lower():
                        enhanced_coverage.append({
                            "coverage": item,
                            "description": details.get("description", ""),
                            "title": details.get("title", product)
                        })
                        break
                else:
                    continue
                break
        else:
            enhanced_coverage.append({
                "coverage": item,
                "description": "Geen specifieke productbeschrijving beschikbaar.",
                "title": "Onbekende verzekering"
            })
    return enhanced_coverage

def parse_analysis_result(content: str) -> Dict[str, Any]:
    result = {
        'current_coverage': [],
        'coverage_gaps': [],
        'recommendations': [],
        'additional_comments': []
    }

    current_section = None
    current_recommendation = None

    try:
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('<bestaande_dekking>'):
                current_section = 'current_coverage'
            elif line.startswith('<dekkingshiaten>'):
                current_section = 'coverage_gaps'
            elif line.startswith('<verzekeringsaanbevelingen>'):
                current_section = 'recommendations'
            elif line.startswith('<aanvullende_opmerkingen>'):
                current_section = 'additional_comments'
            elif line.startswith('</'):
                if current_recommendation:
                    result['recommendations'].append(current_recommendation)
                    current_recommendation = None
                if line.startswith('</verzekeringsaanbevelingen>'):
                    current_section = None
            elif current_section == 'recommendations':
                if line.startswith('Aanbeveling:'):
                    if current_recommendation:
                        result['recommendations'].append(current_recommendation)
                    current_recommendation = {'title': line[12:].strip(), 'description': '', 'rechtvaardiging': '', 'specific_risks': []}
                elif line.startswith('Beschrijving:'):
                    current_recommendation['description'] = line[12:].strip()
                elif line.startswith('Rechtvaardiging:'):
                    current_recommendation['rechtvaardiging'] = line[16:].strip()
                elif line.startswith('Specifieke risico\'s:'):
                    continue
                elif current_recommendation:
                    if not current_recommendation['specific_risks'] or current_recommendation['specific_risks'][-1].startswith('-'):
                        current_recommendation['specific_risks'].append(line)
                    else:
                        current_recommendation['specific_risks'][-1] += ' ' + line
            elif current_section and line and not line.startswith('<'):
                result[current_section].append(line)

        if current_recommendation:
            result['recommendations'].append(current_recommendation)

        return result
    except Exception as e:
        logger.error(f"Error in parse_analysis_result: {str(e)}")
        raise

# Load product descriptions when this module is imported
product_descriptions = load_product_descriptions()

# Initialize OpenAI client (if needed for any legacy functions)
openai_client = None
try:
    from langchain_openai import ChatOpenAI
    openai_client = ChatOpenAI(
        model_name=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        api_key=st.secrets["OPENAI_API_KEY"]
    )
except ImportError:
    logger.warning("Failed to import ChatOpenAI. Some legacy functions may not work.")

# You can add any additional helper functions or initializations here if needed