import os
import simplejson as json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_METHODS = ["Voer tekst in of plak tekst", "Upload tekstbestand", "Upload audiobestand", "Neem audio op"]

def load_config():
    # Voeg hier eventuele aanvullende configuratielogica toe
    return {
        "INPUT_METHODS": INPUT_METHODS,
    }

# New configuration settings

# OpenAI API configuration
OPENAI_MODEL = "gpt-4o-2024-08-06"
OPENAI_TEMPERATURE = 0.1
FEEDBACK_MODEL = "gpt-4o-mini"
FEEDBACK_TEMPERATURE = 0.1

# Logging configuration
LOG_FILE = 'email_generation.log'
LOG_LEVEL = 'DEBUG'

# File paths
PRODUCT_DESCRIPTIONS_FILE = os.path.join(PROJECT_ROOT, '.src', 'product_descriptions.json')
INSURANCE_ADVISOR_PROMPT_FILE = os.path.join(PROJECT_ROOT, 'prompts', 'insurance_advisor_prompt.txt')

# Other configurations
MAX_TOKENS = 10000