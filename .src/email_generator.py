from openai_utils import client

def generate_email(transcript, email_templates):
    prompt = f"""
    Given the following transcript of an advisor's notes:
    
    {transcript}
    
    Generate a professional email to the client based on this information. 
    The email should follow this structure:
    
    1. Greeting
    2. Reference to the recent conversation
    3. Main points from the transcript, elaborated professionally
    4. Suggestion for next steps or a call to action
    5. Professional closing
    
    Use a friendly yet professional tone throughout the email.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional financial advisor assistant, tasked with drafting emails to clients based on the advisor's notes."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content
