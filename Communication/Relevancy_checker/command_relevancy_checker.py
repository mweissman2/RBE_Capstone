import time
from multiprocessing import Queue
from Communication.Function_calling.function_caller import function_caller

def relevancy_subscriber(transcription_q: Queue, response_q: Queue):
    print("relevancy_subscriber started!")
    while True:
        try:
            # Pull audio from queue
            transcription = transcription_q.get(block=True)
            print(f"TRANSCRIPTION RECEIVED!: {transcription}")
            start = time.perf_counter()

            # Check relevancy
            relevancy = relevancy_check(transcription)
            end = time.perf_counter()
            elapsed_time = end - start
            print(f"%%%Relevancy_checker execution time: {elapsed_time} seconds")

            # If relevant, pass to function caller. Else, clarify input
            if relevancy:
                function_caller(transcription)
                relevancy = False
            else:
                # Send for clarification
                pass

        except KeyboardInterrupt:
            break


def relevancy_check(input_string: str):
    """
    Check relevancy of given command
    """
    # Connect to vector database
    # Embed input_string
    # Compare embeddings
    # if thresold > X return True and do function calling (in subscriber)
    # else, return False and send to LLM for clarifying question

    return True

