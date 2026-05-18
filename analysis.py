import os
import json
import google.generativeai as genai
from database import get_connection

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def evaluate_answer(question_text, answer_text, role, expected_skills):
    """
    Evaluates the user's answer using Gemini and returns a structured score.
    """
    if not api_key:
        return {
            "confidence_score": 7,
            "relevance_score": 8,
            "completeness_score": 6,
            "communication_score": 7,
            "feedback": "API Key not configured. This is a dummy feedback. Please add your Gemini API key in the .env file."
        }
        
    prompt = f"""
    You are an expert interviewer evaluating a candidate for a {role} position.
    
    Question asked: "{question_text}"
    Skills being assessed: {expected_skills}
    Candidate's Answer: "{answer_text}"
    
    Evaluate the candidate's answer and provide scores out of 10 for the following categories:
    - relevance_score: How relevant the answer is to the question.
    - completeness_score: How complete the answer is. Did they miss important details?
    - communication_score: Clarity, conciseness, and professionalism of the answer.
    - confidence_score: Inferred confidence based on the phrasing (1-10).
    
    Also provide a constructive "feedback" string (max 3 sentences) explaining the scores and suggesting improvements.
    
    Return the result strictly as a valid JSON object:
    {{
        "relevance_score": int,
        "completeness_score": int,
        "communication_score": int,
        "confidence_score": int,
        "feedback": "string"
    }}
    
    Do not include markdown tags like ```json.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        if text_response.startswith('```json'):
            text_response = text_response[7:-3].strip()
        elif text_response.startswith('```'):
            text_response = text_response[3:-3].strip()
            
        evaluation = json.loads(text_response)
        return evaluation
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return {
            "confidence_score": 5,
            "relevance_score": 5,
            "completeness_score": 5,
            "communication_score": 5,
            "feedback": "Error analyzing answer. Please try again."
        }

def save_evaluation(question_id, evaluation):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO scores (question_id, confidence_score, relevance_score, completeness_score, communication_score, feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            question_id,
            evaluation.get("confidence_score", 0),
            evaluation.get("relevance_score", 0),
            evaluation.get("completeness_score", 0),
            evaluation.get("communication_score", 0),
            evaluation.get("feedback", "")
        ))
        conn.commit()
    except Exception as e:
        print(f"Error saving evaluation: {e}")
    finally:
        conn.close()

def get_performance_metrics(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT 
                i.id as interview_id, i.role, i.timestamp,
                AVG(s.confidence_score) as avg_confidence,
                AVG(s.relevance_score) as avg_relevance,
                AVG(s.completeness_score) as avg_completeness,
                AVG(s.communication_score) as avg_communication
            FROM interviews i
            JOIN questions q ON i.id = q.interview_id
            JOIN scores s ON q.id = s.question_id
            WHERE i.user_id = ?
            GROUP BY i.id
            ORDER BY i.timestamp DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return []
    finally:
        conn.close()
