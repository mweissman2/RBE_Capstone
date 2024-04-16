import time
from multiprocessing import Queue
from Communication.Function_calling.function_caller import function_caller
from Communication.Comms_output.Text_to_speech import tts_via_request
from Communication import utils
import google.generativeai as genai
import numpy as np


def relevancy_subscriber(queue_dict: dict[str, Queue], simMode: bool):

    flag_q = queue_dict['flag']
    transcription_q = queue_dict['transcription']
    response_q = queue_dict['response']

    # Initializations
    chat = start_chat()
    func_list, func_embeddings, example_embeddings = get_embeddings()

    print("relevancy_subscriber started!")
    while True:
        try:
            # Pull audio from queue
            transcription = transcription_q.get(block=True)
            print(f"TRANSCRIPTION RECEIVED!: {transcription}")
            start = time.perf_counter()

            # Check relevancy
            relevancy = relevancy_check(transcription, func_list, func_embeddings, example_embeddings)
            end = time.perf_counter()
            elapsed_time = end - start
            print(f"%%%Relevancy_checker execution time: {elapsed_time} seconds")

            # If relevant, pass to function caller. Else, clarify input
            if relevancy:
                function_caller(transcription, queue_dict, simMode)
            else:
                print("RELEVANCY SUB: No function call")
                response = chat.send_message(
                    transcription + "Keep your response concise."
                )
                tts_via_request("That's not one of my core features, but here's the answer:" + response.text)

        except KeyboardInterrupt:
            break


def relevancy_check(input_str: str, func_list: list, func_embeddings, example_embeddings):
    """
    Check relevancy of given command
    """
    # Connect to vector database
    # Embed input_string
    # Compare embeddings
    # if thresold > X return True and do function calling (in subscriber)
    # else, return False and send to LLM for clarifying question

    # Embed input string
    result = genai.embed_content(
        model="models/embedding-001",
        content=[input_str],
        task_type="semantic_similarity"
    )
    input_embedding = result['embedding'][0]  # Extract embedding for the input string

    max_similarity = -1
    most_relevant_command = None

    # Check similarity for functions and examples
    for i, func in enumerate(func_list):
        # Compare with function description embedding
        similarity = cosine_similarity(input_embedding, func_embeddings[i])

        # Compare with example embeddings
        for example_embedding in example_embeddings[i * len(func['examples']): (i + 1) * len(func['examples'])]:
            similarity = max(similarity, cosine_similarity(input_embedding, example_embedding))

        if similarity > max_similarity:
            max_similarity = similarity
            most_relevant_command = func

    print(f'max similarity: {max_similarity}')
    if max_similarity > 0.70:
        return True
    else:
        return False


def start_chat():
    API_KEY = utils.get_key("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)

    # Define model
    safety_settings = utils.set_gemini_safety_settings()
    model = genai.GenerativeModel(
        'gemini-pro',
        safety_settings=safety_settings)

    # Start chat and send message
    chat = model.start_chat()
    return chat

def get_embeddings():
    # Updated function list with revised descriptions and examples
    func_list = [
        {'name': 'global_nav',
         'description': 'Initiates global navigation from the current location to a specified destination.',
         'examples': ['Start navigating from home to the nearest bus stop.',
                      'Navigate to the grocery store on Main Street.',
                      'Take me to the closest Thai Restaurant',
                      'Lets go to the library',
                      'Can you bring me to the theater?',
                      'Take me to Jimmy Johns',
                      'Lets navigate to TD Bank',
                      'Bring me to Gong Cha Bubble Tea']},

        {'name': 'change_speed',
         'description': 'Adjusts the speed of the system, with options to increase, decrease, or maintain the current velocity.',
         'examples': ['Increase speed to move faster through open spaces.',
                      'Decrease speed to navigate safely in crowded areas.',
                      'Maintain current speed while traversing familiar routes.',
                      'Lets start moving a bit faster',
                      'Woah, lets slow down there']},

        {'name': 'describe_env',
         'description': 'Utilizes system cameras to provide verbal descriptions of the environment surrounding the user.',
         'examples': ['Describe the objects and obstacles in front of me.',
                      'Were in the park right? What does it look like?',
                      'Do I have to worry about any obstacles ahead of me?',
                      'Are there any other people around?']},

        {'name': 'system_stop',
         'description': 'Brings the system to a complete stop, halting all movement and navigation activities.',
         'examples': ['Stop the system in case of an emergency or unexpected obstacle.',
                      'Pause navigation',
                      'Stop!']},

        {'name': 'system_go',
         'description': 'Resumes system operations and navigation after being stopped or paused.',
         'examples': ['Okay, lets keep moving',
                      'Resume system operations',
                      'Sorry I had to tie my shoe, lets keep going now']}
    ]

    # Precompute function embeddings
    content = [func['description'] for func in func_list]
    for func in func_list:
        content.extend(func['examples'])

    result = genai.embed_content(
        model="models/embedding-001",
        content=content,
        task_type="semantic_similarity"
    )

    func_embeddings = result['embedding'][:len(func_list)]  # Extract embeddings for function descriptions
    example_embeddings = result['embedding'][len(func_list):]  # Extract embeddings for examples

    return func_list, func_embeddings, example_embeddings


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))