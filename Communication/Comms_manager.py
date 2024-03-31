import time

from Speech_to_text.ASR_with_wakeword import AudioTranscriber
from Communication.Speech_to_text.classless_ASR import run_audio
from Communication.Speech_to_text.text_reader import text_reader
from Communication.Comms_output import ResponseRefiner, AudioRespond
from multiprocessing import Process, Queue


def run_input_comms():
    # Setup Queues
    audio_chunk_q = Queue()
    text_command_q = Queue()
    response_q = Queue()

    # Set wake-word model path
    keyword_path = "Speech_to_text/Hey-Jimbo_en_windows_v3_0_0.ppn"

    # Create and run audio_listener
    # audio_listener = AudioTranscriber(audio_chunk_q, text_command_q, keyword_path)
    # p1 = Process(target=audio_listener.audio_listener())

    # Need to use classless implementation (pickle-able) for multiprocessing
    p1 = Process(target=run_audio, args=(audio_chunk_q, text_command_q, keyword_path))
    p2 = Process(target=text_reader, args=(text_command_q,))
    p3 = Process(target=ResponseRefiner.response_subscriber, args=(response_q,))

    try:
        # Start Processes
        p1.start()
        p2.start()
        p3.start()

        # Test for process 3
        time.sleep(3)
        print("Type your text for speech synthesis here:")
        for i in range(3):
            desired_text = input()
            AudioRespond.audioRespond(response_q, desired_text)
    except KeyboardInterrupt:
        print("Processes Cancelled")
        # p1.join()
        # p2.join()
        # p3.join()


def main():
    run_input_comms()


if __name__ == "__main__":
    main()
