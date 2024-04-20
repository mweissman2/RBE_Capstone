"""User_Tracking_Controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import Supervisor
from controller import Keyboard
from Communication.CommsManager import *
from Communication.Comms_output.Text_to_speech import tts_via_request
from navigation.global_planner import google_planner, latlong2string, extract_waypoints
from multiprocessing import Process, Queue
import pymap3d
import math


def latlong_2_pos(world_node, latlong: tuple[float, float]) -> tuple[float, float]:
    [lat_ref, long_ref, h_ref] = world_node.getField('gpsReference').getSFVec3f()
    x, y, _ = pymap3d.geodetic2enu(latlong[0], latlong[1], h_ref, lat_ref, long_ref, h_ref)
    return x, y


def calculate_midpoint(point1, point2):
    return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)


def calculate_heading(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle = math.atan2(dy, dx)  # Calculate angle in radians
    return angle


def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


def find_waypoints(world_node, start: tuple[float, float], end: tuple[float, float]):
    # Convert start and end to strings
    start = latlong2string(start)
    end = latlong2string(end)

    # print(f'start: {start}, end: {end}')

    # Get route and extract waypoints
    route = google_planner(start, end)
    waypoints = extract_waypoints(route)

    # Convert waypoints to x-y-z positions
    new_waypoints = [latlong_2_pos(world_node, waypoint) for waypoint in waypoints]
    # print('waypoints', waypoints)
    # print(new_waypoints)
    return new_waypoints


def spawn_waypoints(waypoints, children):
    for waypoint in waypoints:
        children.importMFNodeFromString(-1,
                                        f'DEF WAYPOINT Waypoint {{translation {waypoint[0]} {waypoint[1]} {25} }}')

def spawn_single_line(point1, point2, children):
    midpoint = calculate_midpoint(point1, point2)
    heading = calculate_heading(point1, point2)
    distance = calculate_distance(point1, point2)
    children.importMFNodeFromString(-1,
                                    f'DEF LINE Line {{translation {midpoint[0]} {midpoint[1]} {0} rotation 0 0 1 {heading} size {distance} 1.5 1 }}')

def spawn_lines(start, end, waypoints, children):
    # Spawn line between start and first waypoint
    spawn_single_line(start, waypoints[0], children)

    # Spawn lines between all waypoints
    for i in range(len(waypoints) - 1):
        waypoint1 = waypoints[i]
        waypoint2 = waypoints[i + 1]
        spawn_single_line(waypoint1, waypoint2, children)

    # Spawn line between last waypoint and destination
    spawn_single_line(waypoints[-1], end, children)


def remove_waypoints(robot, waypoints):
    for _ in range(len(waypoints)):
        waypoint_node = robot.getFromDef('WAYPOINT')
        waypoint_node.remove()

def remove_lines(robot, waypoints):
    for _ in range(len(waypoints)+1):
        line_node = robot.getFromDef('LINE')
        line_node.remove()


# Main loop:
# - perform simulation steps until Webots is stopping the controller

def main():
    robot = Supervisor()

    # Get root node
    root_node = robot.getRoot()
    # print(root_node.exportString())
    children_field = root_node.getField('children')
    world_node = children_field.getMFNode(0)

    # create the Robot instance.
    # my_robot = robot.getFromDef('DOG')

    # enable keboard for exiting program
    keyboard = Keyboard()
    keyboard.enable(100)

    # get the time step of the current world.
    timestep = int(robot.getBasicTimeStep())

    # get GPS for position tracking
    GPS = robot.getDevice('gps')
    GPS.enable(timestep)

    # Create and run comms manager
    queue_dict = {'audio': Queue(), 'transcription': Queue(), 'response': Queue(), 'position': Queue(), 'flag': Queue()}
    manager = CommsManager(queue_dict, simMode=True)
    manager.run_processes()

    # Counter for destinations
    first_time_counter = 0
    waypoints = []

    # i = 0
    while robot.step(timestep) != -1:
        # if i == 50:
        #     # print(GPS.getValues()[0], GPS.getValues()[1])
        #     # print(manager.get_status())
        #     i = 0

        # Checks if position is requested, (flag is a dictionary with the flag name and value)
        flag = queue_dict['flag'].get()
        if next(iter(flag)) == 'getPos_request':
            current_pos = GPS.getValues()[0], GPS.getValues()[1]
            queue_dict['position'].put(current_pos)

        # Checks if set_destination requested (with lat/long data)
        elif next(iter(flag)) == 'set_destination':
            destination = (flag['set_destination']['latitude'], flag['set_destination']['longitude'])
            print(f"SET DESTINATION RECEIVED: {destination}")

            # Convert lat/long to position
            x, y = latlong_2_pos(world_node, destination)

            # Spawn destination beacon in Webots
            if first_time_counter == 0:
                children_field.importMFNodeFromString(-1, f'DEF DESTINATION Destination {{ translation {x} {y} {50} }}')
                first_time_counter = 1
            else:
                # Remove current waypoints
                remove_waypoints(robot, waypoints)
                remove_lines(robot, waypoints)

                # Move destination
                destination_node = robot.getFromDef('DESTINATION')
                translation_field = destination_node.getField('translation')
                translation_field.setSFVec3f([x, y, 50])

            # Spawn waypoints to destination
            current_pos = (GPS.getValues()[0], GPS.getValues()[1])
            waypoints = find_waypoints(world_node, current_pos, destination)
            spawn_waypoints(waypoints, children_field)
            spawn_lines(latlong_2_pos(world_node, current_pos), latlong_2_pos(world_node, destination), waypoints, children_field)
            tts_via_request("Route plotted, let me know when you're ready to go")

        # i += 1
        # key = keyboard.getKey()
        # if key==80: #letter p
        #     pass


if __name__ == "__main__":
    main()
