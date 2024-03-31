from multiprocessing import Queue
import google.generativeai as genai
from Communication import utils
from Communication.Comms_output.Text_to_speech import tts_via_request


def response_subscriber(response_q):
    """
    Pulls any desired responses from the queue and sends to response refiner and text to speech
    """
    print("Response Subscriber Started!")
    while True:
        try:
            # Pull audio from queue
            latest_response = response_q.get(block=True)
            refined_response = response_refiner(latest_response)
            tts_via_request(refined_response)
        except KeyboardInterrupt:
            break


def response_refiner(response_raw: str, context: str = "There is a cyclist up ahead coming towards the camera"):
    print("Response picked up")

    # Perform response refinement here
    API_KEY = utils.get_key("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)

    # Model configuration
    generation_config = genai.types.GenerationConfig(
        temperature=0.9,
        top_p=1,
        top_k=1,
        max_output_tokens=2048,
    )

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "block_none"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-pro",
                                  # generation_config=generation_config,
                                  safety_settings=safety_settings)

    prompt_parts = [
        "You are an assistive device for people with visual impairments. Your job is to take a simple command and "
        "ensure the instruction is clear and concise. Follow these rules to help write your response:\n\n1. Use clock "
        "terminology to help describe orientation (example: tree at 5 o'clock)\n2. Numerical based instructions are "
        "helpful but not ideal (example: walk 5 meters)\n3. Do not use degrees to describe turns, instead use simple "
        "commands like left or right\n4. Adding context is perhaps the most important aspect of your response. "
        "Context of the surrounding environment helps the user better understand how to navigate (ex: )\n5. When "
        "adding context to the instructions, ensure you only use the context given to you from the input.",
        "Command: Walk straight for 500 meters and turn 90 degrees to the right",
        "Environmental Context List: You are on a paved sidewalk, there is a large tree ahead on your right with an "
        "overhanging branch",
        "Revised Instruction: Continue walking straight on this sidewalk for a while. You will be turning right "
        "ahead, after the tree on your right. Be careful as you approach the turn, the tree has an overhanging branch "
        "over the sidewalk.",
        "Command: Walk straight for another 200 feet and then turn left on Main Street",
        "Environmental Context List: There are two pedestrians walking on the sidewalk towards the camera",
        "Revised Instruction: We're going to keep walking straight for a bit, and then we're going to be making a "
        "left on main street. There are two people on the sidewalk ahead walking towards you. I'll let you know "
        "before we need to turn.",
        f"Command: {response_raw}",
        f"Environmental Context List: {context}",
        "Revised Instruction: ",
    ]

    refined_response = model.generate_content(prompt_parts)
    print(refined_response.text)

    return refined_response.text
