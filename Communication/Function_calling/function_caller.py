import time
from multiprocessing import Queue
import google.generativeai as genai
import google.ai.generativelanguage as glm
from Communication import utils
from Communication.Comms_output.ImageCaptioner import get_image, describe_image_short, few_shot_describe_image
from Communication.Location_helpers.location_refiner import destination_search
from Communication.Comms_output.Text_to_speech import tts_via_request


def function_caller(input_string: str, queue_dict: dict[str, Queue], simMode):
    start = time.perf_counter()

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
        global_nav(start, response, response_call, queue_dict, simMode)

    elif response_call == 'change_speed':
        change_speed(start, response, response_call, queue_dict)

    elif response_call == 'describe_env':
        describe_env(start, response_call)

    elif response_call == 'system_stop':
        system_stop(start, response_call, queue_dict)

    elif response_call == 'system_go':
        system_go(start, response_call, queue_dict)

    # FOR DEBUGGING ONLY - REMOVE LATER
    else:
        print("No function called")
        try:
            tts_via_request(response.text)
        except ValueError:
            pass
        end_time(start)


def end_time(start: float):
    end = time.perf_counter()
    elapsed_time = end - start
    print(f"%%%Function_caller execution time: {elapsed_time} seconds")


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
         'description': 'Increases or decreases the current velocity of the system. 1 for increase, -1 for decrease. 0 for no change',
         'parameters': {'type_': 'OBJECT',
                        'properties': {
                            'del_v': {'type_': 'INTEGER'}}}}]}
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


def global_nav(start, response, response_call, queue_dict, simMode):
    dest = response.candidates[0].content.parts[0].function_call.args['destination']
    print(f'{response_call} called! Destination: {dest}')

    # Get current position and apply location refinement
    if simMode:
        queue_dict['flag'].put({"getPos_request": ''})
        current_pos = queue_dict['position'].get(block=True)
        # print(f'Picked up in function caller: {current_pos}')
    else:
        current_pos = 42.27377897661122, -71.80928749664702

    # current_pos = get_gps_coords()
    top_place = destination_search(dest, current_pos)
    end_time(start)

    # If in Webots, push destination to flag queue
    if simMode:
        temp_dict = {'set_destination': top_place['location']}
        queue_dict['flag'].put(temp_dict)

    # *** Instead of printing, pass to global nav ***
    print(f"TOP PLACE: {top_place['displayName']['text']} \n"
          f"{top_place['formattedAddress']} \n"
          f"{top_place['location']}")

    tts_via_request(f"Okay! Starting Navigation to {top_place['displayName']['text']}")


def change_speed(start, response, response_call, queue_dict):
    # Changed to Boolean - Increase: True, Decrease: False - Assumes default value for magnitude
    del_v = response.candidates[0].content.parts[0].function_call.args['del_v']
    print(f'{response_call} called! Speed Change: {del_v}')
    end_time(start)

    if del_v == 1:
        tts_via_request("Okay, speeding up")
        queue_dict['flag'].put({"speed_change_request": del_v})
    elif del_v == -1:
        tts_via_request("Okay, slowing down")
        queue_dict['flag'].put({"speed_change_request": del_v})
    else:
        tts_via_request("No change in speed request, try again")
    # Implement change speed call here (with optional param del_v)


def describe_env(start, response_call):
    print(f'{response_call} called!')
    img = get_image('Communication/imgs')
    description = describe_image_short(img)

    end_time(start)
    tts_via_request(description)


def system_stop(start, response_call, queue_dict):
    print(f'{response_call} called!')
    end_time(start)
    tts_via_request("Okay, system stopping")
    queue_dict['flag'].put({"stop_request": ""})


def system_go(start, response_call, queue_dict):
    print(f'{response_call} called!')
    end_time(start)
    tts_via_request("Great, let's go!")
    queue_dict['flag'].put({"go_request": ""})

# For testing
# function_caller('Take me to the closest mall')
