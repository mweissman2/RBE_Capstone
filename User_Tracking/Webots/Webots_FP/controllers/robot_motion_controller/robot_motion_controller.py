"""robot_motion_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import motion_controller  as MC
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

keyboard = Keyboard()
keyboard.enable(100)
    
vx = 0
vy = 0
wz = 0
#create the reference to motion controller
my_controller = MC.MotionController(wheels[0],wheels[1],wheels[2],wheels[3])
 
# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep*4) != -1:
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
    print(vels)
    my_controller.set_velocity(vels)
    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
