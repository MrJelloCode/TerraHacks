
import json
import os

from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def call_gemini_json(prompt: str) -> dict:
    """
    Sends a prompt to Gemini (PaLM) and returns parsed JSON result.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=512),
        ),
    )

    try:
        content = response.text
        print("Gemini response:", content)
        if "```json" in content:
            content = content.split("```json")[-1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print("Error parsing Gemini response:", content, e)
        return None
