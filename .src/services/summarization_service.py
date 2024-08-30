import json
import logging
from typing import List, Dict, Any
import os

import streamlit as st
from autogen_agents import analyze_transcript, generate_email, correction_AI
from config import (
    LOG_FILE, LOG_LEVEL, PRODUCT_DESCRIPTIONS_FILE,
    INPUT_METHODS, load_config
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

def generate_email_wrapper(transcript: str, enhanced_coverage: List[Dict[str, str]], selected_recommendations: List[Dict[str, Any]], identified_insurances: List[str]) -> Dict[str, str]:
    try:
        logging.info("Starting email generation wrapper")

        # Convert coverage and recommendations to JSON strings
        analysis_json = json.dumps(enhanced_coverage, ensure_ascii=False)
        recommendations_json = json.dumps(selected_recommendations, ensure_ascii=False)

        logging.debug(f"Transcript: {transcript}")
        logging.debug(f"Analysis JSON: {analysis_json}")
        logging.debug(f"Recommendations JSON: {recommendations_json}")
        logging.debug(f"Identified insurances: {identified_insurances}")

        if not transcript or not analysis_json or not recommendations_json:
            logging.error("One or more inputs are empty, skipping email generation.")
            raise ValueError("Input data missing or incomplete")

        email_content = generate_email(transcript, analysis_json, recommendations_json, identified_insurances)

        if not email_content['initial_email'] or not email_content['corrected_email']:
            logging.error("Email generation returned empty content.")
            raise ValueError("Email generation did not return any content.")

        return email_content

    except Exception as e:
        logging.error(f"Error in generate_email_wrapper: {str(e)}", exc_info=True)
        raise


# Load product descriptions when this module is imported
product_descriptions = load_product_descriptions()