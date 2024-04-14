import time
import json
import google.generativeai as genai

# Get API KEY
config_path = 'C:/Users/Max/Desktop/api_keys.json'
with open(config_path) as f:
    GEMINI_API_KEY = json.load(f)['GEMINI_API_KEY']
genai.configure(api_key=GEMINI_API_KEY)

# Select Model
model = genai.GenerativeModel('gemini-1.0-pro')

# Initialize chat
chat = model.start_chat(history=[])
chat.send_message("You are working as an assistive device for people with visual impairments. Your job is to take a "
                  "simple command and turn it into something more conversational. Limit your responses to just the "
                  "refined command and nothing more")


def send_chat(text):
    start_time = time.time()
    response = chat.send_message(text)
    end_play_time = time.time()
    play_time = end_play_time - start_time
    print(play_time)

    return response.text


short_text = "Obstacle at 3 o'clock"
medium_text = "Turning left in 300 feet. Straight for 100 feet. Right on 1st street"
print(send_chat(short_text))
