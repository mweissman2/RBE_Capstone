from multiprocessing import Queue
import google.generativeai as genai
import google.ai.generativelanguage as glm
from Communication import utils
from Communication.Comms_output.ImageCaptioner import get_image, describe_image, few_shot_describe_image
from Communication.Location_helpers.location_refiner import destination_search, get_gps_coords
from Communication.Comms_output.AudioRespond import audioRespond
from Communication.Comms_output.Text_to_speech import tts_via_request

def function_caller(input_string: str, response_q: Queue):
    API_KEY = utils.get_key("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)

    # Get available functions
    funcs = create_functions()

    # Define model
    safety_settings = utils.set_gemini_safety_settings()
    model = genai.GenerativeModel(
        'gemini-pro',
        tools=funcs,
        safety_settings=safety_settings)

    # Start chat and send message
    chat = model.start_chat()
    response = chat.send_message(
        input_string
    )

    # Parse response to call function
    response_call = response.candidates[0].content.parts[0].function_call.name

    if response_call == 'global_nav':
        dest = response.candidates[0].content.parts[0].function_call.args['destination']
        print(f'global_nav called! Destination: {dest}')

        # Get current position and apply location refinement
        current_pos = get_gps_coords()
        top_place = destination_search(dest, current_pos)

        # *** Instead of printing, pass to global nav ***
        print(f"TOP PLACE: {top_place['displayName']['text']} \n"
              f"{top_place['formattedAddress']} \n"
              f"{top_place['location']}")
        tts_via_request(f"Okay! Starting Navigation to {top_place['displayName']['text']}")

    elif response_call == 'get_next_waypoint_on_route':
        print('get_next_waypoint_on_route called!')

    elif response_call == 'describe_env':
        print('describe_env called!')
        img = get_image('Communication/imgs')
        description = describe_image(img)
        tts_via_request(description)

    # FOR DEBUGGING ONLY - REMOVE LATER
    else:
        print("No function called")
        print(response.text)


def create_functions():
    """
    Creates all functions/tools to provide to the LLM
    :return: list of functions
    """
    func_list = []

    global_nav = {'function_declarations': [
        {'name': 'global_nav',
         'description': 'Begins global navigation from starting position to destination',
         'parameters': {'type_': 'OBJECT',
                        'properties': {
                            'destination': {'type_': 'STRING'},
                            'b': {'type_': 'NUMBER'}},
                        'required': ['destination']}}]}
    func_list.append(global_nav)

    # Need to remove this one
    get_next_waypoint_on_route = {'function_declarations': [
        {'name': 'get_next_waypoint_on_route',
         'description': 'Checks the current position using GPS and the current global navigator to identify where it '
                        'is on the path and output the next path waypoint',
         'parameters': {'type_': 'OBJECT',
                        'properties': {
                            'position': {'type_': 'ARRAY'},
                            'navigation_map': {'type_': 'OBJECT'}},
                        'required': ['position', 'navigation_map']}}]}
    func_list.append(get_next_waypoint_on_route)

    describe_env = {'function_declarations': [
        {'name': 'describe_env',
         'description': 'Used to describe the current environment around the user using system cameras'}]}
    func_list.append(describe_env)

    return func_list

# For testing
# function_caller('Take me to the closest mall')
