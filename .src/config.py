import json

def load_config():
    with open('templates/email_templates.json', 'r') as f:
        email_templates = json.load(f)
    
    return {
        'email_templates': email_templates
    }