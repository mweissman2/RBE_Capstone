import time
from Communication.Speech_to_text.classless_ASR import run_audio
from Communication.Speech_to_text.text_reader import text_reader
from Communication.Comms_output import ResponseRefiner, AudioRespond
from multiprocessing import Process, Queue


class CommsManager():
    def __init__(self):
        self.audio_chunk_q = Queue()
        self.text_command_q = Queue()
        self.response_q = Queue()

        # Set wake-word model path
        self.keyword_path = "Communication/Speech_to_text/Hey-Jimbo_en_windows_v3_0_0.ppn"

        self.processes = self.init_processes()

    def init_processes(self):
        # Create and run audio_listener
        # audio_listener = AudioTranscriber(audio_chunk_q, text_command_q, keyword_path)
        # p1 = Process(target=audio_listener.audio_listener())
        p = []
        p.append(Process(target=run_audio, args=(self.audio_chunk_q, self.text_command_q, self.keyword_path)))
        p.append(Process(target=text_reader, args=(self.text_command_q,)))
        p.append(Process(target=ResponseRefiner.response_subscriber, args=(self.response_q,)))
        return p

    def run_processes(self):
        try:
            # Start Processes
            for process in self.processes:
                process.start()

            # Test for process 3
            time.sleep(3)
            print("Type your text for speech synthesis here:")
        #     for i in range(3):
            desired_text = input()
            AudioRespond.audioRespond(self.response_q, desired_text)
        except KeyboardInterrupt:
            print("Processes Cancelled")
            # p1.join()
            # p2.join()
            # p3.join()

    def get_status(self):
        return "running"


def main():
    manager = CommsManager()
    manager.run_processes()


if __name__ == "__main__":
    main()
