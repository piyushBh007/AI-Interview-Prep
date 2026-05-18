import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_questions(role, experience, difficulty, num_questions=5):
    """
    Generates interview questions using Gemini based on role, experience, and difficulty.
    """
    if not api_key:
        # Fallback dummy questions if API key is not set
        return [
            {"type": "Technical", "text": f"Explain a challenging {role} problem you solved.", "skills": "problem-solving"},
            {"type": "HR", "text": "Where do you see yourself in 5 years?", "skills": "vision, communication"}
        ]
    
    prompt = f"""
    You are an expert technical interviewer and HR manager. 
    Generate exactly {num_questions} interview questions for a {role} position.
    The candidate has an experience level of: {experience}.
    The interview difficulty should be: {difficulty}.
    Include a mix of Technical, Behavioral, and HR questions.
    
    Return the result strictly as a valid JSON array of objects, where each object has:
    - "type": (String) e.g., "Technical", "Behavioral", "HR", "Aptitude"
    - "text": (String) The actual question
    - "skills": (String) Comma separated skills being assessed
    
    Do not include any markdown formatting like ```json or ``` in the response. Return raw JSON array only.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        if text_response.startswith('```json'):
            text_response = text_response[7:-3].strip()
        elif text_response.startswith('```'):
            text_response = text_response[3:-3].strip()
            
        questions = json.loads(text_response)
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        # Fallback
        return [
            {"type": "Technical", "text": "Tell me about a time you faced a difficult challenge at work.", "skills": "problem-solving, resilience"},
            {"type": "HR", "text": "Why do you want this role?", "skills": "motivation"}
        ]
