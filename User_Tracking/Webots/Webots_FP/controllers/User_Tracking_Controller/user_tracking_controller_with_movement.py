"""User_Tracking_Controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor
import Gimbal_Controller as GC
import robot_motion_controller.Motion_Controller as MC
from controller import Keyboard
import csv
import os

cwd = os.path.dirname(__file__)

#find the robot and user nodes
robot = Supervisor()
#get ID of user for tracking.
user_node = robot.getFromDef('USER')
user_id = user_node.getId()
# create the Robot instance.
#my_robot = robot.getFromDef('DOG')

#logging data from file
csv_file = open(cwd + '\\User_Tracking_Data.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
header = ['Actual X Pos', 'Actual Y Pos', 'Measured X Pos', 'Measured Y Pos', 'Timestep' 'Out_of_range']
csv_writer.writerow(header)

#enable keboard for exiting program and controlling
keyboard = Keyboard()
keyboard.enable(100)

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
camera_timestep = 32*3

#get the wheel objects
wheels = []
wheel_names = ['front_left_wheel', 'front_right_wheel', 'back_left_wheel', 'back_right_wheel']
for name in wheel_names:
    wheels.append(robot.getDevice(name))

#get the sensor objects
rgb_camera = []
depth_camera = []
gimbal_joints = []

rgb_camera = (robot.getDevice('RGB_camera'))
depth_camera = (robot.getDevice('range_finder'))
rgb_camera.enable(camera_timestep)
depth_camera.enable(camera_timestep)

#get joint objects
joint_names = ['gimbal_j1_motor', 'gimbal_j2_motor']
for names in joint_names:
    gimbal_joints.append(robot.getDevice(names))

#get GPS for position tracking
GPS = robot.getDevice('gps')
GPS.enable(timestep)

#get IMU for heading tracking
heading = robot.getDevice('imu')
heading.enable(timestep)

#initialize motion controller
my_controller = MC.Motion_Controller(wheels[0],wheels[1],wheels[2],wheels[3], GPS, heading)
#initialize user tracker
user_tracker = GC.Gimbal_Controller(rgb_camera, depth_camera, gimbal_joints,camera_timestep)
#enables computer vision and sets the ID for user recognition
user_tracker.enable_tracking(True)
user_tracker.set_user_id(user_id)
print("Tracking started")



# Main loop:
# - perform simulation steps until Webots is stopping the controller
i = 0
vx = 0
vy = 0
wz = 0
while robot.step(timestep) != -1:
    #set motor control
    key = keyboard.getKey()
    if key == ord('I'):
        vx += 0.5
    if key == ord('L'):
        vx -= 0.5
    if key == ord('K'):
        vy += 0.5
    if key == ord(':'):
        vy -= 0.5
    if key == ord('I'):
        wz += 0.5
    if key == ord('P'):
        wz -= 0.5

    vels = [vx, vy, wz]
    print(vels)
    my_controller.set_velocity(vx,vy,wz)


    if i == 3:
        measured_position, user_out_of_range = user_tracker.run()
        #print(measured_position)
        # log data
        # get measured data
        robot_location =GPS.getValues()
        curr_time = str(robot.getTime())
        meas_x_pos = str(measured_position[0]+robot_location[0])
        meas_y_pos = str(measured_position[1]+robot_location[1])

        #get position of user model
        user_position = user_node.getPosition()
        act_x_pos = str(user_position[0])
        act_y_pos = str(user_position[1])

        line = [act_x_pos,act_y_pos, meas_x_pos, meas_y_pos, curr_time, user_out_of_range]
        csv_writer.writerow(line)

        i = 0
    i += 1
    key = keyboard.getKey()
    if key==80: #letter p
        break

    pass

# Enter here exit cleanup code.
csv_file.close()

#read csv file and plot with matplotlib
exec(open(cwd+ '\\user_tracking_plotter.py').read())
