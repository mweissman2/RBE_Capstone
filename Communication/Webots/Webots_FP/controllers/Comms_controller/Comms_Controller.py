"""User_Tracking_Controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import Supervisor
from controller import Keyboard, Speaker
from Communication.CommsManager import *
from multiprocessing import Process, Queue
import numpy as np
import pymap3d
import os


def latlong_2_pos(world_node, latlong: tuple[float, float]) -> tuple[float, float, float]:
    """
    Converts lat/long to x,y,z
    :param latlong: a tuple of latitude, longitude
    :return: a tuple of floats (x,y,z)
    """
    [lat_ref, long_ref, _] = world_node.getField('gpsReference').getSFVec3f()
    lat_diff_meters = (latlong[0] - lat_ref) * 111132.92
    long_diff_meters = (latlong[1] - long_ref) * (111321.377 * np.cos(np.radians(lat_ref)))
    return lat_diff_meters, long_diff_meters, 0


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

    # get speaker for output comms
    # speaker = robot.getDevice('speaker')

    # Create and run comms manager
    queue_dict = {'audio': Queue(), 'transcription': Queue(), 'response': Queue(), 'position': Queue(), 'flag': Queue()}
    manager = CommsManager(queue_dict, simMode=True)
    manager.run_processes()

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
            # x, y, z = latlong_2_pos(world_node, destination)
            [lat_ref, long_ref, h_ref] = world_node.getField('gpsReference').getSFVec3f()
            x, y, _ = pymap3d.geodetic2enu(destination[0], destination[1], h_ref, lat_ref, long_ref, h_ref)

            # Spawn destination beacon in Webots
            # if counter == 0:
            # children_field.importMFNodeFromString(-1, f'DEF DESTINATION Destination {{ translation {x} {y} {50} }}')
            destination_node = robot.getFromDef('DESTINATION')
            translation_field = destination_node.getField('translation')
            translation_field.setSFVec3f([x, y, 50])

        # i += 1
        # key = keyboard.getKey()
        # if key==80: #letter p
        #     pass


if __name__ == "__main__":
    main()
