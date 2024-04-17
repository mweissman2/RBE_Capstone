import multiprocessing
import sys
import time
from Communication.Speech_to_text.classless_ASR import run_audio
# from Communication.Speech_to_text.text_reader import text_reader
from Communication.Relevancy_checker import command_relevancy_checker
from Communication.Comms_output import ResponseRefiner, AudioRespond
from multiprocessing import Process, Queue


class CommsManager:
    def __init__(self, queue_dict: dict[str, Queue] = None, simMode: bool = False):
        self.simMode = simMode
        if queue_dict is None:
            self.queue_dict = {'audio': Queue(), 'transcription': Queue(), 'response': Queue(), 'position': Queue(), 'flag': Queue()}
        else:
            self.queue_dict = queue_dict

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
        p.append(Process(target=run_audio, args=(self.queue_dict, self.keyword_path)))
        p.append(Process(target=command_relevancy_checker.relevancy_subscriber, args=(self.queue_dict, self.simMode)))
        p.append(Process(target=ResponseRefiner.response_subscriber, args=(self.queue_dict,)))
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
            if not self.simMode:
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

    def get_robot_pos(self):
        # *** NEW IDEA - CREATE FLAG QUEUE, function in manager to set flags, which can be picked up in controller
        # controller can call getGPSPosition - maybe push position to another queue to be picked up by function caller?

        # NEWER IDEA - move all queues to controller script, have it check queues at each time step instead of using subscribers
        # GPS = self.robot.getDevice('gps')
        # GPS.enable(32 * 3)
        # return GPS.getValues()[0], GPS.getValues()[1]
        pass


def main():
    manager = CommsManager()
    manager.run_processes()


if __name__ == "__main__":
    main()
