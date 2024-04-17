"""supervisor_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor
from controller import Keyboard
import random as randint
import numpy as np 
import time
import csv
import math

#class to control pedestrian.
class Pedestrian ():
    """Control a Pedestrian PROTO."""

    def __init__(self, model):
        #set offset from the frame of the robot and other parameters for following
        self.robot_offset = [-2, -0.1, 0]
        self.robot_to_follow = []
        self.kpid = [1,0,0.5]
        self.previous_error = [0, 0, 0]
        self.error_sum = [0,0,0]
        self.object = model

        """Constructor: initialize constants."""
        self.BODY_PARTS_NUMBER = 13
        self.WALK_SEQUENCES_NUMBER = 8
        self.ROOT_HEIGHT = 1.27
        self.CYCLE_TO_DISTANCE_RATIO = 0.22
        self.speed = 1.15
        self.current_height_offset = 0
        self.joints_position_field = []
        self.joint_names = [
            "leftArmAngle", "leftLowerArmAngle", "leftHandAngle",
            "rightArmAngle", "rightLowerArmAngle", "rightHandAngle",
            "leftLegAngle", "leftLowerLegAngle", "leftFootAngle",
            "rightLegAngle", "rightLowerLegAngle", "rightFootAngle",
            "headAngle"
        ]
        self.height_offsets = [  # those coefficients are empirical coefficients which result in a realistic walking gait
            -0.02, 0.04, 0.08, -0.03, -0.02, 0.04, 0.08, -0.03
        ]
        self.angles = [  # those coefficients are empirical coefficients which result in a realistic walking gait
            [-0.52, -0.15, 0.58, 0.7, 0.52, 0.17, -0.36, -0.74],  # left arm
            [0.0, -0.16, -0.7, -0.38, -0.47, -0.3, -0.58, -0.21],  # left lower arm
            [0.12, 0.0, 0.12, 0.2, 0.0, -0.17, -0.25, 0.0],  # left hand
            [0.52, 0.17, -0.36, -0.74, -0.52, -0.15, 0.58, 0.7],  # right arm
            [-0.47, -0.3, -0.58, -0.21, 0.0, -0.16, -0.7, -0.38],  # right lower arm
            [0.0, -0.17, -0.25, 0.0, 0.12, 0.0, 0.12, 0.2],  # right hand
            [-0.55, -0.85, -1.14, -0.7, -0.56, 0.12, 0.24, 0.4],  # left leg
            [1.4, 1.58, 1.71, 0.49, 0.84, 0.0, 0.14, 0.26],  # left lower leg
            [0.07, 0.07, -0.07, -0.36, 0.0, 0.0, 0.32, -0.07],  # left foot
            [-0.56, 0.12, 0.24, 0.4, -0.55, -0.85, -1.14, -0.7],  # right leg
            [0.84, 0.0, 0.14, 0.26, 1.4, 1.58, 1.71, 0.49],  # right lower leg
            [0.0, 0.0, 0.42, -0.07, 0.07, 0.07, -0.07, -0.36],  # right foot
            [0.18, 0.09, 0.0, 0.09, 0.18, 0.09, 0.0, 0.09]  # head
        ]

        self.max_velocity = 1.4;

        #set initial value of parameters
        #used in keyboard control
        self.sim_time = 0
        self.angles = 0
        self.num_steps = 0
        self.action = 0
        self.current_step = 0
        self.rotation = 0
        self.velocity = 0.7
        self.keyboard = Keyboard()
        self.keyboard.enable(1000)
        print('initalizing done')


    def execute_step(self):
        return 0

    def get_next_step(self):
        return 0

    def animate(self):
        return 0;

    #finds the set point based on position behind the robot, and then makes the user go towards that at a fixed velocity
    def update_position(self, timestep):
        #gets user and robot pose and orientation
        robot_pose = self.robot_to_follow.getPosition()
        robot_orientation = self.robot_to_follow.getField('rotation').getSFRotation()
        curr_pose = self.object.getPosition()
        curr_orientation = self.object.getField('rotation').getSFRotation()

        time_delta = timestep/1000
        #figures out the location of the desired set point behind/around the robot.
        x_set_point =  self.robot_offset[0]*np.cos(robot_orientation[3]) - self.robot_offset[1]*np.sin(robot_orientation[3]) + robot_pose[0]
        y_set_point = self.robot_offset[0]*np.sin(robot_orientation[3])+self.robot_offset[1]*np.cos(robot_orientation[3]) + robot_pose[1]

        #makes a vector to point from one to the other
        x_error = x_set_point - curr_pose[0]
        y_error = y_set_point - curr_pose[1]

        #error case where we get close to just not move
        if abs(x_error) < 0.01:
            x_error = 0
        if abs(y_error) < 0.01:
            y_error = 0

        if x_error == 0 and y_error == 0:
            mag = 1
        else:
            mag = np.sqrt(x_error**2 + y_error**2)
        #angle error isnt used
        #angle_error = robot_orientation[3] - curr_orientation[3]

        #points the user towards the robot
        angle = math.atan2(y_error,x_error)

        #update position
        dx = self.kpid[0]*(x_error/mag)*self.velocity*time_delta
        dy = self.kpid[0]*(y_error/mag)*self.velocity*time_delta
        new_trans = [curr_pose[0]+dx, curr_pose[1]+dy, curr_pose[2]]
        new_rot = [curr_orientation[0], curr_orientation[1], curr_orientation[2], angle]
        return new_trans, new_rot
    def get_keyboard_value(self):
        stop_boolean = False
        key = self.keyboard.getKey()

        if key == 88: #if x then stop
            self.velocity = 0
            stop_boolean = True
            print("person stopped")
        elif key == 87: #if w then speed up
            self.velocity += 0.05
            if self.velocity >= self.max_velocity:
               self.velocity = self.max_velocity
            print(self.velocity)
        elif key == 83: #if s then slow down
            self.velocity -= 0.05
            if self.velocity < 0:
                self.velocity = 0
            print(self.velocity)
        elif key == 65:
            #rotate left
            self.rotation +=0.17 #10 degrees
            #print('rotating left')
        elif key == 68:
            #rotate right
            self.rotation -= 0.17  # 10 degrees
            #print('rotating right')
            
        return stop_boolean

TIME_STEP = 20

robot = Supervisor()
dog = robot.getFromDef('DOG')
user_node = robot.getFromDef('USER')

controller = Pedestrian(user_node)
controller.robot_to_follow = dog
root_node = robot.getRoot()
children_field = root_node.getField('children')


user_translation = user_node.getField('translation')
user_rotation = user_node.getField('rotation')
i = 0
while robot.step(TIME_STEP) != -1:
    if i == 3:
        controller.get_keyboard_value()
        i = 0
    #position = user_node.getPosition()
    #rotation = user_rotation.getSFRotation()
    new_pose, new_rotation = controller.update_position(TIME_STEP)
    user_translation.setSFVec3f(new_pose)
    user_rotation.setSFRotation(new_rotation)
    i += 1


