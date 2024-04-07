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
        print(f'{response_call} called! Destination: {dest}')

        # Get current position and apply location refinement
        current_pos = get_gps_coords()
        top_place = destination_search(dest, current_pos)

        # *** Instead of printing, pass to global nav ***
        print(f"TOP PLACE: {top_place['displayName']['text']} \n"
              f"{top_place['formattedAddress']} \n"
              f"{top_place['location']}")
        tts_via_request(f"Okay! Starting Navigation to {top_place['displayName']['text']}")

    elif response_call == 'change_speed':
        # Changed to Boolean - Increase: True, Decrease: False - Assumes default value for magnitude
        del_v = response.candidates[0].content.parts[0].function_call.args['del_v']
        print(f'{response_call} called! Speed Change: {del_v}')
        if del_v:
            tts_via_request("Okay, speeding up")
        elif not del_v:
            tts_via_request("Okay, slowing down")
        # Implement change speed call here (with optional param del_v)

    elif response_call == 'describe_env':
        print(f'{response_call} called!')
        img = get_image('Communication/imgs')
        description = describe_image(img)
        tts_via_request(description)

    elif response_call == 'system_stop':
        print(f'{response_call} called!')
        tts_via_request("Okay, system stopping")

    elif response_call == 'system_go':
        print(f'{response_call} called!')
        tts_via_request("Great, let's go!")

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
                            'destination': {'type_': 'STRING'}},
                        'required': ['destination']}}]}
    func_list.append(global_nav)

    # Need to remove this one
    change_speed = {'function_declarations': [
        {'name': 'change_speed',
         'description': 'Increases or decreases the current velocity of the system. True for increase, False for decrease.',
         'parameters': {'type_': 'OBJECT',
                        'properties': {
                            'del_v': {'type_': 'BOOLEAN'}}}}]}
    func_list.append(change_speed)

    describe_env = {'function_declarations': [
        {'name': 'describe_env',
         'description': 'Used to describe the current environment around the user using system cameras'}]}
    func_list.append(describe_env)

    system_stop = {'function_declarations': [
        {'name': 'system_stop',
         'description': 'Requests system to come to a full stop'}]}
    func_list.append(system_stop)

    system_go = {'function_declarations': [
        {'name': 'system_go',
         'description': 'Requests system start up.'}]}
    func_list.append(system_go)

    return func_list

# For testing
# function_caller('Take me to the closest mall')
