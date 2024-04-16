# from controller import *        # controller is name of Webots API
#

import googlemaps
from datetime import datetime
import queue
from Communication import utils

def extract_api_key():
    # extracts API key on your desktop for use in google_planner
    #  you have to specify the file path, it will be different per person
    # DO NOT SAVE API KEY FILE ON GITHUB
    api_file_path = r'C:\Users\outdo\Desktop'

    try:
        with open(api_file_path, 'r') as file:
            for line in file:
                if 'MAPS_API_KEY' in line:
                    api_key = line.strip().split('=')[1].strip()
                    return api_key
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("Error:", e)


def google_planner(start, goal):
    '''
    For global planner we plan to use google-maps API to retrieve global path
    start:
    Must be string of address that is passed to the directions method

    goal:
    Must be string of address that is passed to the directions method
    '''
    # api_key = extract_api_key()

    api_key = utils.get_key("GOOGLE_MAPS_API_KEY")
    gmaps = googlemaps.Client(key=api_key)  # key should be kept secret on server

    # Geocoding an address
    # geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

    # Look up an address with reverse geocoding
    # reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

    # Request directions via public transit
    now = datetime.now()
    '''Full explanation of arguments:
    https://github.com/googlemaps/google-maps-services-python/blob/master/googlemaps/directions.py
    https://googlemaps.github.io/google-maps-services-python/docs/index.html#googlemaps.Client.directions
    '''

    # call directions method, set parameter to walking, departure_time
    # returns list of routes
    directions_result = gmaps.directions(start,
                                         goal,
                                         mode="walking",
                                         departure_time=now,
                                         )

    # Validate an address with address validation
    # addressvalidation_result = gmaps.addressvalidation(['1600 Amphitheatre Pk'],
    #                                                    regionCode='US',
    #                                                    locality='Mountain View',
    #                                                    enableUspsCass=True)

    return directions_result  # can return json with fields for routes, and directions


def interpret_directions(route):
    """
    Here the function takes the route generated by Google Maps and creates a series
    of directions for the robot



    json file returns geocoordinates for each leg
    webots GPS can be aligned based on map import

    example return JSON from google maps directions method:
    https://developers.google.com/maps/documentation/directions/get-directions#DirectionsResponses

    """
    path_coord_list = []
    path_coord_list = queue.Queue()
    # routes is a returned dict of routes
    # first access routes key, then legs key
    # first hiearchy of legs is waypoint to waypoint called 'legs', second hierarchy is steps per waypoint called 'steps'
    for route_step in route['legs']['steps']:
        robot_waypoint = route_step['start_location']
        # maybe we dont need all the end coordinates because they match start coordinates for each step
        # step_end_coor = route_step['end_location']          # example:  "end_location": { "lat": 41.8769003, "lng": -87.6297353 },
        # pile coordinates into stack
        path_coord_list.put(robot_waypoint)

def latlong2string(latlong: tuple[float, float]) -> str:
    """
    Converts latitude longitude tuple to string for googlemaps search
    :param latlong: tuple
    :return: str
    """
    latitude, longitude = latlong
    return str(latitude) + ", " + str(longitude)


def extract_waypoints(route) -> list[tuple[float, float]]:
    """
    Takes in route from googlemaps and parses to waypoints
    Note: waypoints here are the end_locations for each step
    :param route: route from googlemaps routes
    :return: list of waypoints
    """
    legs = [route_step['legs'] for route_step in route][0][0]
    steps = legs['steps']
    end_locations = [step['end_location'] for step in steps]

    waypoints = [(end_location['lat'], end_location['lng']) for end_location in end_locations]

    return waypoints

