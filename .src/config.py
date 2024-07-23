import os
import json

INPUT_METHODS = ["Voer tekst in of plak tekst", "Upload tekstbestand", "Upload audiobestand", "Neem audio op"]

def load_config():
    # Voeg hier eventuele aanvullende configuratielogica toe
    return {
        "INPUT_METHODS": INPUT_METHODS,
    }