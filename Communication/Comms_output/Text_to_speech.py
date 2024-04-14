from elevenlabs.client import ElevenLabs
from elevenlabs import play
from Communication import utils
import requests


def setup():
    # Get API KEY
    API_KEY = utils.get_key("ELEVENLABS_API_KEY")
    client = ElevenLabs(
        api_key=API_KEY
    )
    return API_KEY, client


# Eleven Labs workflow
def tts(text_to_play):
    API_KEY, client = setup()
    audio = client.generate(
        # api_key="YOUR_API_KEY", (Defaults to os.getenv(ELEVEN_API_KEY))
        text=text_to_play,
        voice="Bill",
        model="eleven_turbo_v2"
    )

    play(audio)


def tts_via_request(text_to_play: str):
    """
    Makes direct POST request to ElevenLabs and plays response Audio
    Current Voice: Rachel
    """
    API_KEY, client = setup()

    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    querystring = {"output_format": "mp3_22050_32"}
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    data = {
        "text": text_to_play,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    # Make request and play response
    response = requests.post(url, json=data, headers=headers, params=querystring)
    play(response.content)

# Samples
# tts("Go straight for another 100 feet and then turn right on Main Street")
# tts_via_request("Go straight for another 100 feet and then turn right on Main Street")
# NOTE: POST request seems a bit faster than using python API
