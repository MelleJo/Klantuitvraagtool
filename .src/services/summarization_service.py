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
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the JSON file
        json_path = os.path.join(current_dir, '..', 'product_descriptions.json')
        
        # Print debugging information
        print(f"Current working directory: {os.getcwd()}")
        print(f"Attempting to load file from: {json_path}")
        
        # Check if the file exists
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"The file does not exist at {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logging.info(f"Successfully loaded product descriptions from {json_path}")
        return data
    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {str(e)}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in 'product_descriptions.json': {str(e)}")
        return {}
    except Exception as e:
        logging.error(f"Unexpected error while loading 'product_descriptions.json': {str(e)}")
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



# Load product descriptions when this module is imported
product_descriptions = load_product_descriptions()