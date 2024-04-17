"""User_Tracking_Controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import Supervisor
from controller import Keyboard
import Gimbal_Controller as GC
import csv

def main():
    robot = Supervisor()
    #get ID of user for tracking.
    user_node = robot.getFromDef('USER')
    user_id = user_node.getId()
    # create the Robot instance.
    #my_robot = robot.getFromDef('DOG')

    #logging data from file
    csv_file = open('User_Tracking_Data.csv', 'w', newline='')
    csv_writer = csv.writer(csv_file)
    header = ['Actual X Pos', 'Actual Y Pos', 'Timestep', 'Measured X Pos', 'Measured Y Pos', 'Timestep']
    csv_writer.writerow(header)

    #enable keboard for exiting program
    keyboard = Keyboard()
    keyboard.enable(100)


    # get the time step of the current world.
    timestep = int(robot.getBasicTimeStep())
    camera_timestep = 32*3


    rgb_camera = []
    depth_camera = []
    gimbal_joints = []

    #get sensors
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
    GPS.enable(camera_timestep)


    tracker = GC.Gimbal_Controller(rgb_camera, depth_camera, gimbal_joints,camera_timestep)
    #enables computer vision and sets the ID for user recognition
    tracker.enable_tracking(True)
    tracker.set_user_id(user_id)
    print("Tracking started")
    # Main loop:
    # - perform simulation steps until Webots is stopping the controller
    i = 0
    while robot.step(timestep) != -1:
        # Read the sensors:
        if i == 3:
            measured_position = tracker.run()
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

            line = [act_x_pos,act_y_pos, curr_time, meas_x_pos, meas_y_pos, curr_time]
            csv_writer.writerow(line)

            i = 0
        i += 1
        key = keyboard.getKey()
        print(key)
        if key==80: #letter p
            break

        pass

    # Enter here exit cleanup code.
    csv_file.close()

if __name__ == "__main__":
    main()