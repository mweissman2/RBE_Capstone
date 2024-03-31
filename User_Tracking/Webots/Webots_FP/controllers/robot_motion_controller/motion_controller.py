from controller import robot
import numpy as np

class MotionController:
    def __init__(self, wheel1, wheel2, wheel3, wheel4):
        self.inside_wheel_front = wheel1 #front left
        self.inside_wheel_back = wheel4 #back right
        self.outside_wheel_front = wheel2 #front right
        self.outside_wheel_back = wheel3 #back left

        self.current_position = [0,0]
        self.current_heading = 0
        self.wheel_radius = 3.15
        self.l_x = 0.5
        self.l_y = 0.5

    #input array is [vx,vy,wz]
    def set_velocity(self, velocity_array):
        wheel_velocities = self.inverse_kinematics(velocity_array[0], velocity_array[1], velocity_array[2])

        #need to be set to inf for velocity control to work
        self.inside_wheel_front.setPosition(float('inf'))
        self.inside_wheel_back.setPosition(float('inf'))
        self.outside_wheel_front.setPosition(float('inf'))
        self.outside_wheel_back.setPosition(float('inf'))

        #set velocities
        self.inside_wheel_front.setVelocity(wheel_velocities[0])
        self.outside_wheel_front.setVelocity(wheel_velocities[1])
        self.outside_wheel_back.setVelocity(wheel_velocities[2])
        self.inside_wheel_back.setVelocity(wheel_velocities[3])


    def set_forward_velocity(self, velocity):
        self.inside_wheel_front.setPosition(float('inf'))
        self.inside_wheel_back.setPosition(float('inf'))

        self.outside_wheel_front.setPosition(float('inf'))
        self.outside_wheel_back.setPosition(float('inf'))

        self.inside_wheel_front.setVelocity(velocity)
        self.inside_wheel_back.setVelocity(velocity)

        self.outside_wheel_front.setVelocity(-velocity)
        self.outside_wheel_back.setVelocity(-velocity)


    def set_forward_position(self, distance):
        return 0

    def set_left_velocity(self, velocity):
        return 0

    def set_left_position(self, distance):
        return 0

    def set_right_velocity(self, velocity):

        return 0

    def set_right_position(self, distance):
        return 0

    def set_turn_velocity(self, velocity):
        return 0

    def set_turn_position(self, angle):
        return 0

    def set_turn_virtual_center(self, angle):
        return 0

    def set_turn_virtual_center_velocity(self, velocity):
        return 0

    def get_current_position(self):
        return self.current_position

    def set_current_position(self, new_position):
        self.current_position = new_position

    def get_heading(self):
        return self.current_heading

    def set_heading(self, new_heading):
        self.current_heading = new_heading

    def get_encoder_reading(self, wheel):
        return 0

    def at_goal_position(self, goal_position):
        #checkfoward kinematics more weight
        #check GPS position less weight


        # then check compass
        #if within error bounds, move to next spot
        #else keep moving
        #
        return False

    def inverse_kinematics(self, x_vel, y_vel, z_vel):
        inv_kin = np.array([[1, -1, -(self.l_x+self.l_y)],
                            [1, 1, (self.l_x+self.l_y)],
                            [1, 1, -(self.l_x+self.l_y)],
                            [1, -1, (self.l_x+self.l_y)]], dtype=np.float64)

        vels = np.array([x_vel, y_vel, z_vel]).reshape(3,1)
        [wfl, wfr, wbl, wbr] = np.matmul(inv_kin, vels)
        return [wfl, wfr, wbl, wbr]