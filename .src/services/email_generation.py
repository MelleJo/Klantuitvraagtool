# email_generation.py
import logging
import json
from typing import List, Dict, Any
from autogen_agents import generate_email, correction_AI
import streamlit as st

def load_insurance_specific_instructions(identified_insurances: List[str]) -> str:
    """
    Load specific instructions for the identified insurances from guideline files.
    
    Args:
    identified_insurances (List[str]): List of identified insurance types.
    
    Returns:
    str: A string containing specific instructions for the identified insurances.
    """
    insurance_file_mapping = {
        "auto": "autoverzekering.txt",
        "liability": "particuliere_aansprakelijkheid.txt",
        "property": "gebouwen.txt",
        "contents": "inboedel_prive.txt",
        "business_contents": "inboedel_inventaris_goederen.txt",
        "business_liability": "avb.txt",
        "business_interruption": "bedrijfsschade.txt",
        "cyber": "cyber.txt",
        "travel": "reis_prive.txt",
        "business_travel": "reis_zakelijk.txt",
        "legal": "rechtsbijstand.txt",
        "health": "zorgverzekering_prive.txt",
        "pension": "pensioen_aov.txt",
        "transport": "transportverzekering.txt",
        "home": "woonhuis.txt"
    }

    instructions = "Here are specific instructions for the identified insurance types:\n\n"

    for insurance in identified_insurances:
        if insurance.lower() in insurance_file_mapping:
            file_name = insurance_file_mapping[insurance.lower()]
            try:
                file_content = read_file(f".src/insurance_guidelines/{file_name}")
                instructions += f"Instructions for {insurance} insurance:\n{file_content}\n\n"
            except Exception as e:
                logging.error(f"Error reading guideline file for {insurance}: {str(e)}")
                instructions += f"Unable to load specific instructions for {insurance} insurance.\n\n"
        else:
            instructions += f"No specific guideline file found for {insurance} insurance.\n\n"

    return instructions

def read_file(file_path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
    file_path (str): Path to the file to be read.
    
    Returns:
    str: Contents of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_email_wrapper(
    transcript: str,
    enhanced_coverage: List[Dict[str, str]],
    selected_recommendations: List[Dict[str, Any]],
    identified_insurances: List[str],
    guidelines: str,
    product_descriptions: Dict[str, Any]
) -> Dict[str, str]:
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

        # Include detailed descriptions in the email generation process
        detailed_descriptions = st.session_state.get('detailed_descriptions', {})
        detailed_descriptions_json = json.dumps(detailed_descriptions, ensure_ascii=False)

        # Load insurance-specific instructions
        insurance_specific_instructions = load_insurance_specific_instructions(identified_insurances)

        email_content = generate_email(
            transcript, 
            analysis_json, 
            recommendations_json, 
            identified_insurances, 
            product_descriptions, 
            detailed_descriptions_json,
            insurance_specific_instructions
        )

        if not email_content['initial_email'] or not email_content['corrected_email']:
            logging.error("Email generation returned empty content.")
            raise ValueError("Email generation did not return any content.")

        # Apply correction AI with the loaded guidelines and transcript
        corrected_email = correction_AI(
            email_content['initial_email'],
            guidelines,
            product_descriptions,
            insurance_specific_instructions,
            transcript,
            detailed_descriptions_json
        )

        email_content['corrected_email'] = corrected_email

        return email_content

    except Exception as e:
        logging.error(f"Error in generate_email_wrapper: {str(e)}", exc_info=True)
        raise