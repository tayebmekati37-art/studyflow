import google.generativeai as genai
import os
import json
import re

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
def extract_json(text):
    """Extract JSON from Gemini response (handles markdown code blocks)."""
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        content = match.group(1)
    else:
        content = text
    try:
        return json.loads(content.strip())
    except json.JSONDecodeError:
        return {"error": "Could not parse JSON", "raw": text}

def generate_summary(text, source_lang='auto', target_lang='en'):
    """Generate a summary in target language."""
    prompt = f"""
    You are an AI study assistant. Summarize the following text (language: {source_lang}) in {target_lang}. 
    Keep the summary concise (max 200 words) and highlight key points.
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return response.text

def generate_flashcards(text, source_lang='auto', count=10):
    """Generate flashcards (front/back) for study."""
    prompt = f"""
    Extract important concepts, terms, or questions from the following text. 
    For each, create a flashcard with:
    - front: A question or term (in the original language, unless specified)
    - back: The answer or definition (in English, unless specified)
    Return a JSON array of objects with keys: "front", "back".
    Limit to {count} items.
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return extract_json(response.text)

def generate_quiz(text, source_lang='auto', num_questions=5):
    """Generate multiple-choice quiz questions."""
    prompt = f"""
    Create {num_questions} multiple-choice questions based on the following text. 
    Return a JSON array with objects containing:
    - "question": the question (in English)
    - "options": array of 4 possible answers
    - "correct": the correct answer (must match one of the options)
    - "explanation": brief explanation
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return extract_json(response.text)
