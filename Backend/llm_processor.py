# llm_processor.py

import os
import json
import re
from google import genai

API_KEY = "AIzaSyCZKjKcX1bSwlPNTwxSGWUnnV1S5aC-0Z0"

if not API_KEY:
    raise ValueError("Please set GEMINI_API_KEY as environment variable.")

client = genai.Client(api_key=API_KEY)


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None


def extract_requirements(query: str):

    prompt = f"""
You are a strict JSON generator.

Extract structured hiring requirements.

Return ONLY valid JSON.
No explanations.
No markdown.

Format:
{{
  "technical_skills": [],
  "behavioral_skills": [],
  "role_type": ""
}}

Query:
{query}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt,
        )

        json_text = extract_json(response.text.strip())

        if json_text:
            return json.loads(json_text)

    except Exception as e:
        print("LLM Error:", e)

    return {
        "technical_skills": [],
        "behavioral_skills": [],
        "role_type": ""
    }



