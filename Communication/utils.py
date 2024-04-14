import json
from openai import OpenAI
import google.generativeai as genai
import elevenlabs


def get_key(key_name):
    """
    Gets API key (and returns client for OpenAI)
    """
    config_path = 'C:/Users/Max/Desktop/api_keys.json'
    with open(config_path) as f:
        KEY = json.load(f)[key_name]

    # if key_name == "OPENAI_API_KEY":
    #     client = OpenAI(
    #         api_key=KEY
    #     )
    #     return client
    # elif key_name == "GEMINI_API_KEY":
    #     genai.configure(api_key=KEY)
    #
    # elif key_name == "ELEVENLABS_API_KEY":
    #     elevenlabs.set_api_key(KEY)

    return KEY

def set_gemini_safety_settings():
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "block_none"
        },
    ]
    return safety_settings
