"""User_Tracking_Controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import Supervisor
from controller import Keyboard, Speaker
from Communication.CommsManager import *
import os



# Main loop:
# - perform simulation steps until Webots is stopping the controller
def main():
    robot = Supervisor()
    # get ID of user for tracking.
    user_node = robot.getFromDef('USER')
    user_id = user_node.getId()
    # create the Robot instance.
    # my_robot = robot.getFromDef('DOG')

    # enable keboard for exiting program
    keyboard = Keyboard()
    keyboard.enable(100)

    # get the time step of the current world.
    timestep = int(robot.getBasicTimeStep())
    camera_timestep = 32 * 3

    # get GPS for position tracking
    GPS = robot.getDevice('gps')
    GPS.enable(camera_timestep)

    # get speaker for output comms
    speaker = robot.getDevice('speaker')


    # Create and run comms manager
    # manager = CommsManager('webots')
    manager = CommsManager()
    manager.run_processes()

    # Quick test for multiprocessing
    # num_q = Queue()
    # gps_q = Queue()
    # p1 = Process(target=process1, args=(gps_q,))
    # p2 = Process(target=process2, args=(num_q,))
    # p1.start()
    # p2.start()

    i = 0
    j = 0
    while robot.step(timestep) != -1:
        if i == 50:
            print(GPS.getValues()[0])
            # Speaker.playSound(speaker, speaker, audio_file, 1.0, 1.0, 0, False)
            # print(manager.get_status())
            i = 0

        i += 1
        key = keyboard.getKey()
        if key==80: #letter p
            pass

if __name__ == "__main__":
    main()