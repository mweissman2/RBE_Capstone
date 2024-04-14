import multiprocessing
import sys
import time
from Communication.Speech_to_text.classless_ASR import run_audio
# from Communication.Speech_to_text.text_reader import text_reader
from Communication.Relevancy_checker import command_relevancy_checker
from Communication.Comms_output import ResponseRefiner, AudioRespond
from multiprocessing import Process, Queue


class CommsManager():
    def __init__(self):
        self.audio_chunk_q = Queue()
        self.transcription_q = Queue()
        self.response_q = Queue()

        # Set wake-word model path
        self.keyword_path = "Communication/Speech_to_text/Hey-Jimbo_en_windows_v3_0_0.ppn"

        # Initialize processes
        self.processes = self.init_processes()

        self.is_running = True

    def init_processes(self):
        # Create and run audio_listener
        # audio_listener = AudioTranscriber(audio_chunk_q, text_command_q, keyword_path)
        # p1 = Process(target=audio_listener.audio_listener())

        p = []
        p.append(Process(target=run_audio, args=(self.audio_chunk_q, self.transcription_q, self.keyword_path)))
        p.append(Process(target=command_relevancy_checker.relevancy_subscriber, args=(self.transcription_q, self.response_q)))
        p.append(Process(target=ResponseRefiner.response_subscriber, args=(self.response_q,)))
        return p

    def run_processes(self):
        try:
            # Start Processes
            for process in self.processes:
                process.start()
            event = multiprocessing.Event()

            # Test for process 3
            # time.sleep(3)
            # print("Type your text for speech synthesis here:")
            # #     for i in range(3):
            # desired_text = input()
            # AudioRespond.audioRespond(self.response_q, desired_text)

            # End processes on exit (CTRL+C)
            while True:
                if event.is_set():
                    print("Exiting all processes...")
                    for process in self.processes:
                        process.terminate()
                    sys.exit(1)
                time.sleep(2)

        except KeyboardInterrupt:
            self.is_running = False
            print("***Processes Ended***")

    def get_status(self):
        return self.is_running


def main():
    manager = CommsManager()
    manager.run_processes()


if __name__ == "__main__":
    main()
