"""User_Tracking_Controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor, gps
import Gimbal_Controller as GC
import User_Tracking.Webots.Webots_FP.controllers.robot_motion_controller.Motion_Controller as MC
import User_Tracking.Webots.Webots_FP.controllers.obstacle_detector.obstacle_detector as OD
from Communication.CommsManager import *
from multiprocessing import Process, Queue
import numpy as np
from controller import Keyboard
import csv
import os
import pymap3d as pymap

def main():
    cwd = os.path.dirname(__file__)

    # find the robot and user nodes
    robot = Supervisor()
    root = robot.getRoot()
    root_children = root.getField('children')
    world_node = root_children.getMFNode(0)
    gps_reference = world_node.getField('gpsReference').getSFVec3f()
    print(gps_reference)
    ell = pymap.Ellipsoid(6378137.0, 6356752.31424518)
    # get ID of user for tracking.
    user_node = robot.getFromDef('USER')
    user_id = user_node.getId()
    # create the Robot instance.
    # my_robot = robot.getFromDef('DOG')

    # logging data from file
    csv_file = open(cwd + '\\User_Tracking_Data.csv', 'w', newline='')
    csv_writer = csv.writer(csv_file)
    header = ['Actual X Pos', 'Actual Y Pos', 'Measured X Pos', 'Measured Y Pos', 'Timestep', 'Distance', 'Out_of_range',
              'Tracking_flag', 'Velocity_mag', 'Velocity_angle']
    csv_writer.writerow(header)

    # enable keboard for exiting program and controlling
    keyboard = Keyboard()
    keyboard.enable(100)

    # get the time step of the current world.
    # timestep = int(robot.getBasicTimeStep())
    timestep = 20
    camera_timestep = 200

    # get the wheel objects
    wheels = []
    wheel_names = ['front_left_wheel', 'front_right_wheel', 'back_left_wheel', 'back_right_wheel']
    for name in wheel_names:
        wheels.append(robot.getDevice(name))

    # get the sensor objects
    rgb_camera = []
    depth_camera = []
    gimbal_joints = []

    rgb_camera = (robot.getDevice('RGB_camera'))
    depth_camera = (robot.getDevice('range_finder'))
    rgb_camera.enable(camera_timestep)
    depth_camera.enable(camera_timestep)

    front_camera = robot.getDevice('front_camera')
    front_camera.enable(camera_timestep)

    # get joint objects
    joint_names = ['gimbal_j1_motor', 'gimbal_j2_motor']
    for names in joint_names:
        gimbal_joints.append(robot.getDevice(names))

    # get GPS for position tracking
    GPS = robot.getDevice('gps')
    GPS.enable(timestep)

    # get IMU for heading tracking
    heading = robot.getDevice('imu')
    heading.enable(timestep)

    # initialize motion controller
    my_controller = MC.Motion_Controller(wheels[0], wheels[1], wheels[2], wheels[3], GPS, heading)
    # initialize user tracker
    user_tracker = GC.Gimbal_Controller(rgb_camera, depth_camera, gimbal_joints, camera_timestep)
    # enables computer vision and sets the ID for user recognition
    user_tracker.enable_tracking(True)
    user_tracker.set_user_id(user_id)

    # initialize the obstacle detector
    front_cam_tf_matrix = np.array([[1, 0, 0, 0.305],
                                    [0, 1, 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]])
    front_obs_detect = OD.ObstacleDetector(front_camera, front_cam_tf_matrix, camera_timestep)
    front_obs_detect.camera_location = 'front'

    dog_node = robot.getFromDef("DOG")
    robot_orientation = dog_node.getField('rotation')

    # Comms Manager Intialization
    # Create and run comms manager
    queue_dict = {'audio': Queue(), 'transcription': Queue(), 'response': Queue(), 'position': Queue(), 'flag': Queue()}
    manager = CommsManager(queue_dict, simMode=True)
    manager.run_processes()


    # Main loop:
    # - perform simulation steps until Webots is stopping the controller
    i = 0
    vx = 0
    vy = 0
    wz = 0
    first = True
    done_flag = False
    scene_descript_flag = True
    goal_location = [-5, 0, 0]
    curr_time = 0

    while robot.step(timestep) != -1:
        curr_time = robot.getTime()
        robot_location = dog_node.getPosition()
        robot_angle = robot_orientation.getSFRotation()[3]

        # manual control of robot
        key = keyboard.getKey()

        if key == ord('I'):  # forward
            vx += 0.1
        if key == ord('K'):  # backward
            vx -= 0.1
        if key == ord('J'):  # left or right
            vy += 0.1
        if key == ord('L'):  # left or right
            vy -= 0.1
        if key == ord('U'):  # rotate
            wz += 0.1
        if key == ord('O'):  # rotate
            wz -= 0.1
        if key == ord('M'):  # stops all movement
            vx = 0
            vy = 0
            wz = 0

        vels = [vx, vy, wz]
        # print(vels)
        # my_controller.set_velocity(vx,vy,wz)

        # code block for sending one waypoint and moving the robot
        if first:
            my_controller.set_current_position(robot_location, True)
            my_controller.new_plan_trajectory([robot_location[0] + goal_location[0], robot_location[1] + goal_location[1], robot_angle + goal_location[2]], 5, curr_time)
            first = False

        if not done_flag:
            done_flag = my_controller.move(curr_time, robot_location)
        else:
            my_controller.set_velocity(vx, vy, wz)

            if scene_descript_flag:
                next_direction = 'Go straight for another 20 meters and then turn right'
                obstacle_context = front_obs_detect.get_camera_context()
                print(str(obstacle_context))
                queue_dict['response'].put([next_direction, str(obstacle_context)])
                scene_descript_flag = False


        if i == 5:
            obstacle_dictionary = front_obs_detect.get_camera_obstacles(robot_location)
            measured_position, user_out_of_range, tracking_flag, vm, va = user_tracker.run()
            # measured_position, user_out_of_range, tracking_flag, vm, va = [[1, 1], False, True, 0, 0]
            # print(measured_position)
            # log data
            # get measured data
            # robot_location_lat_long = GPS.getValues()
            # robot_location = pymap.geodetic2enu(robot_location_lat_long[0],
            #                                        robot_location_lat_long[1],
            #                                        robot_location_lat_long[2],
            #                                        gps_reference[0],
            #                                        gps_reference[1],
            #                                        gps_reference[2],
            #                                    ell)
            curr_time = str(robot.getTime())
            # meas_x_pos = str(measured_position[0]+robot_location[0])
            meas_x_pos = str(
                measured_position[0] * np.cos(robot_angle) - measured_position[1] * np.sin(robot_angle) + robot_location[0])
            # meas_y_pos = str(measured_position[1]+robot_location[1])
            meas_y_pos = str(
                measured_position[1] * np.cos(robot_angle) + measured_position[0] * np.sin(robot_angle) + robot_location[1])
            distance = np.sqrt(np.square(measured_position[0]) + np.square(measured_position[1]))

            # get position of user model
            user_position = user_node.getPosition()
            act_x_pos = str(user_position[0])
            act_y_pos = str(user_position[1])

            line = [act_x_pos, act_y_pos, meas_x_pos, meas_y_pos, curr_time, distance, float(user_out_of_range),
                    float(tracking_flag), str(vm), str(va)]
            csv_writer.writerow(line)

            i = 0
        i += 1
        key = keyboard.getKey()
        if key == ord('{'):  # letter {
            break

        pass

    # Enter here exit cleanup code.
    csv_file.close()

    # read csv file and plot with matplotlib
    exec(open(cwd + '\\user_tracking_plotter.py').read())


if __name__ == "__main__":
    main()