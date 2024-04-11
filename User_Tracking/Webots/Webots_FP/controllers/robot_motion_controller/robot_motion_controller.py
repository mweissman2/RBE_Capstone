"""robot_motion_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import Motion_Controller as MC
from controller import Keyboard

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
wheels = []
wheel_names = ['front_left_wheel', 'front_right_wheel', 'back_left_wheel', 'back_right_wheel']
for name in wheel_names:
    wheels.append(robot.getDevice(name))

GPS = robot.getDevice('gps')
GPS.enable(timestep)
keyboard = Keyboard()
keyboard.enable(100)

heading = robot.getDevice('imu')
heading.enable(timestep)
    
vx = 0
vy = 0
wz = 0
#create the reference to motion controller
my_controller = MC.Motion_Controller(wheels[0],wheels[1],wheels[2],wheels[3], GPS, heading)

first = True
# Main loop:
iterations = 0
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep*3) != -1:
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()
    key = keyboard.getKey()
    if key == ord('W'):
        vx += 0.5
    if key == ord('S'):
        vx -= 0.5
    if key == ord('A'):
        vy += 0.5
    if key == ord('D'):
        vy -= 0.5
    if key == ord('Q'):
        wz += 0.5
    if key == ord('E'):
        wz -= 0.5

    vels = [vx,vy,wz]
    #print(vels)
    #my_controller.set_velocity(vx,vy,wz)


    #if first:
    #    my_controller.set_current_position()
    #    my_controller.new_plan_trajectory([4,4,0.5],5)
    #    first = False

    #done_flag = my_controller.move()
    #if done_flag == False:
    #    print("Robot")

    if first:
        next_point = input("What is the desired point")
        my_controller.plan_trajectory([2,4,0.36], [0.25,0.25,0], 10)
        first = False

    done_flag = my_controller.send_next_step(0.5)
    if done_flag == False:
        my_controller.plan_trajectory([0,0,0], [0.25,0.25,0], 10)

    iterations += 1
    if iterations >= 10:
        iterations = 0
        my_controller.plot()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
