import logging
import json
from typing import List, Dict, Any
from autogen_agents import generate_email, correction_AI
import streamlit as st

def load_insurance_specific_instructions(identified_insurances: List[str]) -> str:
    """
    Load specific instructions for the identified insurances from guideline files.
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

    # Add the required closing message instruction
    instructions += "\nIMPORTANT: Always end the email with a personalized version of this message:\n"
    instructions += "'Wij nemen binnenkort contact met je op om dit te bespreken. Als je voor die tijd vragen hebt, "
    instructions += "kun je natuurlijk altijd contact met me opnemen.\n\n"
    instructions += "Met vriendelijke groet,\n[NAAM ADVISEUR]\nVeldhuis Advies\nTel: 0578-699760'\n"

    return instructions

def read_file(file_path: str) -> str:
    """
    Read the contents of a file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def filter_recommendations_by_selection(
    recommendations: List[Dict[str, Any]], 
    selected_recommendations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter recommendations to only include selected ones.
    """
    selected_titles = {rec['title'] for rec in selected_recommendations if rec.get('selected', False)}
    return [rec for rec in recommendations if rec['title'] in selected_titles]

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
        
        # Strictly filter recommendations to only use selected ones
        selected_recommendations = [rec for rec in selected_recommendations if rec.get('selected', True)]
        
        # Convert coverage and recommendations to JSON strings
        analysis_json = json.dumps(enhanced_coverage, ensure_ascii=False)
        recommendations_json = json.dumps(selected_recommendations, ensure_ascii=False)

        logging.debug(f"Number of selected recommendations: {len(selected_recommendations)}")
        logging.debug(f"Selected recommendations: {recommendations_json}")
        
        if not transcript or not analysis_json or not recommendations_json:
            logging.error("One or more inputs are empty, skipping email generation.")
            raise ValueError("Input data missing or incomplete")

        # Filter detailed descriptions to only include selected recommendations
        detailed_descriptions = st.session_state.get('detailed_descriptions', {})
        filtered_descriptions = {
            title: desc for title, desc in detailed_descriptions.items()
            if any(rec['title'] == title and rec.get('selected', False) for rec in selected_recommendations)
        }
        detailed_descriptions_json = json.dumps(filtered_descriptions, ensure_ascii=False)

        # Filter identified insurances based on selected recommendations
        filtered_insurances = [
            ins for ins in identified_insurances
            if any(rec['title'].lower() in ins.lower() and rec.get('selected', False) 
                  for rec in selected_recommendations)
        ]
        
        # Load insurance-specific instructions for filtered insurances
        insurance_specific_instructions = load_insurance_specific_instructions(filtered_insurances)

        # Generate initial email
        email_content = generate_email(
            transcript, 
            analysis_json, 
            recommendations_json, 
            filtered_insurances, 
            product_descriptions, 
            detailed_descriptions_json,
            insurance_specific_instructions
        )

        if not email_content.get('initial_email') or not email_content.get('corrected_email'):
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

        # Ensure the closing message is present
        if "Wij nemen binnenkort contact met je op" not in corrected_email:
            closing_message = ("\n\nWij nemen binnenkort contact met je op om dit te bespreken. "
                             "Als je voor die tijd vragen hebt, kun je natuurlijk altijd contact met me opnemen.\n\n"
                             "Met vriendelijke groet,\n[NAAM ADVISEUR]\nVeldhuis Advies\nTel: 0578-699760")
            corrected_email += closing_message

        email_content['corrected_email'] = corrected_email

        return email_content

    except Exception as e:
        logging.error(f"Error in generate_email_wrapper: {str(e)}", exc_info=True)
        raise