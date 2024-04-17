import pvporcupine
import pyaudio
from Communication import utils
import struct
import speech_recognition as sr
from openai import OpenAI
from multiprocessing import Queue
import io


class AudioTranscriber:
    def __init__(self, audio_q, text_q, keyword_path):
        # Setup OpenAI
        self.OPEN_AI_KEY = utils.get_key("OPENAI_API_KEY")
        self.PORCUPINE_API_KEY = utils.get_key("PORCUPINE_API_KEY")
        self.client = OpenAI(api_key=self.OPEN_AI_KEY)

        # Setup wakeword path
        self.keyword_path = keyword_path

        # Set up recorder and mic
        self.mic = sr.Microphone()
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = 1000
        self.recorder.dynamic_energy_threshold = False
        with self.mic:
            self.recorder.adjust_for_ambient_noise(self.mic)

        self.chunk_time = 2
        self.phrase_time = None

        # Setup queues
        self.audio_in_queue = audio_q
        self.text_command_queue = text_q

        # Initialize transcription
        self.transcription = ['']

    def audio_listener(self):
        """
        Starts a new thread for listening in background and calls transcriber in loop
        """
        # Set up wakeword listener
        print("Listening...")
        porcupine = pvporcupine.create(
            access_key=self.PORCUPINE_API_KEY,
            keyword_paths=[self.keyword_path]
        )
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length)

        # Run listener loop forever
        while True:
            # Read audio stream to check for wakeword
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)

            # If keyword detected
            if keyword_index >= 0:
                print("Wake-word detected, say something!")
                # Perform speech recognition
                with self.mic as source:
                    # Save audio and push to queue
                    audio = self.recorder.listen(source)
                    self.audio_in_queue.put(audio)

                    # Try to transcribe
                    try:
                        transcription = self.transcriber()
                    except KeyboardInterrupt:
                        break
                    except Queue.queue.empty:
                        print("TIME OUT: No input detected")
                        break

                # Push transcription to text queue and print
                self.text_command_queue.put(transcription)
                print(f"Transcription: {transcription}")

    def transcriber(self):
        """
        Pop audio from queue and run Whisper API call to transcribe
        Pushes new transcription to text command queue
        """
        # Pull audio from queue
        audio_data = self.audio_in_queue.get(block=True, timeout=5)

        # Convert audio data to WAV format and name (this is important for openAI call to work)
        buffer = io.BytesIO(audio_data.get_wav_data())
        buffer.name = 'file.wav'

        # Read the transcription.
        print("Processing...")
        result = self.client.audio.transcriptions.create(
            model="whisper-1",
            language="en",
            file=buffer,
            response_format="text",
        )
        print("Processed!")

        return result
