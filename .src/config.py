import os

INPUT_METHODS = ["Voer tekst in of plak tekst", "Upload tekst", "Upload audio", "Neem audio op"]

def load_config():
    # Add any additional configuration loading logic here
    return {
        "INPUT_METHODS": INPUT_METHODS,
    }