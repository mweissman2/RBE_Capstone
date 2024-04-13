"""User_Tracking_Controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import Supervisor
from controller import Keyboard, Speaker
from Communication.CommsManager import *
from multiprocessing import Process, Queue
import os



# Main loop:
# - perform simulation steps until Webots is stopping the controller

def main():
    robot = Supervisor()
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
    GPS.enable(timestep)

    # get speaker for output comms
    # speaker = robot.getDevice('speaker')

    # Create and run comms manager
    queue_dict = {'audio': Queue(), 'transcription': Queue(), 'response': Queue(), 'position': Queue(), 'flag': Queue()}
    manager = CommsManager(queue_dict, simMode=True)
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
            # print(GPS.getValues()[0], GPS.getValues()[1])
            # print(manager.get_status())
            i = 0

        # Checks if position is requested
        flag = queue_dict['flag'].get()
        if flag == 'getPos_request':
            current_pos = GPS.getValues()[0], GPS.getValues()[1]
            queue_dict['position'].put(current_pos)
            print(flag)
        i += 1
        key = keyboard.getKey()
        if key==80: #letter p
            pass

if __name__ == "__main__":
    main()