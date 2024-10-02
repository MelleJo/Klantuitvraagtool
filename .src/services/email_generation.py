# email_generation.py
import logging
import json
from typing import List, Dict, Any
from autogen_agents import generate_email, correction_AI

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

        email_content = generate_email(transcript, analysis_json, recommendations_json, identified_insurances, product_descriptions)

        if not email_content['initial_email'] or not email_content['corrected_email']:
            logging.error("Email generation returned empty content.")
            raise ValueError("Email generation did not return any content.")

        # Apply correction AI with the loaded guidelines
        corrected_email = correction_AI(
            email_content['initial_email'],
            guidelines,
            product_descriptions,
            load_insurance_specific_instructions(identified_insurances)
        )
        email_content['corrected_email'] = corrected_email

        return email_content

    except Exception as e:
        logging.error(f"Error in generate_email_wrapper: {str(e)}", exc_info=True)
        raise