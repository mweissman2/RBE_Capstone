import pvporcupine
import pyaudio
from Communication import utils
import struct
import speech_recognition as sr
from openai import OpenAI
import io
from multiprocessing import Queue


def setup_wakeword_listener(keyword_path):
    """
  Sets up the wakeword listener and returns necessary objects.
  """
    # Setup OpenAI
    OPEN_AI_KEY = utils.get_key("OPENAI_API_KEY")
    PORCUPINE_API_KEY = utils.get_key("PORCUPINE_API_KEY")
    client = OpenAI(api_key=OPEN_AI_KEY)

    # Setup wakeword listener
    porcupine = pvporcupine.create(
        access_key=PORCUPINE_API_KEY,
        keyword_paths=[keyword_path]
    )
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length)
    return client, porcupine, pa, audio_stream


def listen_for_wakeword(porcupine, audio_stream):
    """
  Listens for the wakeword in the audio stream.
  """
    while True:
        # Read audio stream to check for wakeword
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)

        # If keyword detected
        if keyword_index >= 0:
            return True


def record_audio(mic, recorder, audio_q):
    """
  Records audio from the microphone.
  """
    print("Wake-word detected, say something!")
    with mic as source:
        # Perform speech recognition
        audio = recorder.listen(source)
        audio_q.put(audio)


def transcribe_audio(client, audio_q):
    """
  Transcribes audio data using the Whisper API.
  """
    audio_data = audio_q.get(block=True, timeout=5)

    # Convert audio data to WAV format and name (this is important for openAI call to work)
    buffer = io.BytesIO(audio_data.get_wav_data())
    buffer.name = 'file.wav'

    # Read the transcription.
    print("Processing...")
    result = client.audio.transcriptions.create(
        model="whisper-1",
        language="en",
        file=buffer,
        response_format="text",
    )
    print("Processed!")
    return result


def run_audio(audio_q, transcription_q, keyword_path):
    """
  Main function that coordinates wakeword detection, recording, and transcription.
  """
    # Setup
    try:
        client, porcupine, pa, audio_stream = setup_wakeword_listener(keyword_path)
        mic = sr.Microphone()
        recorder = sr.Recognizer()
        recorder.energy_threshold = 1000
        recorder.dynamic_energy_threshold = False
        with mic:
            recorder.adjust_for_ambient_noise(mic)
    except OSError:
        print("ASR Process Cancelled Early")

    print("ASR Started! Listening...")
    while True:
        try:
            # Listen for wakeword
            if listen_for_wakeword(porcupine, audio_stream):
                # Record audio
                record_audio(mic, recorder, audio_q)

                # Transcribe audio
                transcription = transcribe_audio(client, audio_q)

                # Push transcription to queue
                transcription_q.put(transcription)
                print(f"Transcription: {transcription}")
        except KeyboardInterrupt:
            break

# For testing only
# audio_q = Queue()
# text_q = Queue()
# keyword_path = "Hey-Jimbo_en_windows_v3_0_0.ppn"
# run_audio(audio_q, text_q, keyword_path)