# To run this code you need to install the following dependencies:
# pip install google-genai

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATE = (
    "You are an expert Instagram content creator. Generate creative, human-like, non-repetitive captions with emojis"
    "for the image described as: \"{description}\".\n"
    "Return ONLY a valid JSON array with these styles: 'Evocative & Broad', 'Intriguing & Question-Based', "
    "'Short & Punchy with Keywords', 'A touch of poetic', 'Focus on the feeling', 'Witty', 'Inspirational', 'Minimalist'.\n"
    "Each style must have exactly 2 captions."
)

# Create the client ONCE
_CLIENT = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
_MODEL = "gemma-3n-e2b-it"

# Small response sizes for latency
_GENERATE_CONFIG = types.GenerateContentConfig(
    max_output_tokens=800,  # enough for 8 styles x 2 captions
    temperature=0.9,
)


def generate(generated_caption: str):
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=PROMPT_TEMPLATE.format(description=generated_caption))],
        )
    ]

    full_response = ""
    for chunk in _CLIENT.models.generate_content_stream(
        model=_MODEL,
        contents=contents,
        config=_GENERATE_CONFIG,
    ):
        if chunk.text:
            full_response += chunk.text

    cleaned_text = (
        full_response.strip()
        .replace("```json", "")
        .replace("```", "")
        .replace("None", "")
        .strip()
    )
    try:
        parsed_captions = json.loads(cleaned_text)
        return parsed_captions
    except json.JSONDecodeError:
        # best-effort minimal recovery: wrap single object into list if needed
        if cleaned_text.startswith("{") and cleaned_text.endswith("}"):
            try:
                return [json.loads(cleaned_text)]
            except Exception:
                pass
        return None
