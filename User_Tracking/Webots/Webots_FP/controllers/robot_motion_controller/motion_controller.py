from controller import robot
import numpy as np

class MotionController:
    def __init__(self, wheel1, wheel2, wheel3, wheel4):
        self.inside_wheel_front = wheel1 #front left
        self.inside_wheel_back = wheel4 #back right
        self.outside_wheel_front = wheel2 #front right
        self.outside_wheel_back = wheel3 #back left

        self.current_position = [0,0,0]
        self.current_velocity = [0,0,0]
        self.goal_position = [0,0,0]
        self.error_epsilon = 0.1
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

    def at_goal_position(self):
        if abs(self.current_position[0]-self.goal_position[0]) < self.error_epsilon:
            if abs(self.current_position[1]-self.goal_position[1]) < self.error_epsilon:
                if abs(self.current_position[2]-self.goal_position[2]) < self.error_epsilon*5: #heading error is less important
                    return True

        return False
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


    def quintic_trajectory(self, x_i, x_f, xd_i, xd_f, xdd_i, xdd_f, t, steps):
        inputs = np.array([x_i, x_f, xd_i, xd_f, xdd_i, xdd_f]).reshape(6,1)

        matrix = np.array([[0,0,0,0,0,1],
                           [np.power(t,5), np.power(t,4), np.power(t,3), np.power(t,2), 1],
                          [0,0,0,0,1,0],
                          [5*np.power(t,4), 4*np.power(t,3), 3*np.power(t,2), 2*t, 1, 0],
                          [0,0,0,2,0,0],
                          [20*np.power(t,3), 12*np.power(t,2), 6*t, 2, 0, 0]])
        coeffs = np.matmul(np.linalg.inv(matrix), inputs)

        #linear spacing of trajectory
        time_steps = np.linspace(0, t, steps)
        x_traj = coeffs[0]*np.power(time_steps,5)+coeffs[1]*np.power(time_steps,4)+coeffs[2]*np.power(time_steps,3)+coeffs[3]*np.power(time_steps,2)+coeffs[4]*time_steps+coeffs[5]
        xd_traj = 5*coeffs[0]*np.power(time_steps,4)+4*coeffs[1]*np.power(time_steps,3)+3*coeffs[2]*np.power(time_steps,2)+2*coeffs[3]*time_steps+coeffs[4]
        xdd_traj = 20*coeffs[0]*np.power(time_steps,3)+12*coeffs[1]*np.power(time_steps,2)+6*coeffs[2]*time_steps+2*coeffs[3]

        return x_traj, xd_traj, xdd_traj

    def plan_trajectory(self, final_points, end_velocity, time):
        [x_traj, xd_traj, xdd_traj] = self.quintic_trajectory(self.current_position[0], final_points[0], self.current_velocity[0],end_velocity[0],0,0,time, 10)
        [y_traj, yd_traj, ydd_traj] = self.quintic_trajectory(self.current_position[1], final_points[1], self.current_velocity[1],end_velocity[1],0,0,time, 10)
        [w_traj, wd_traj, wdd_traj] = self.quintic_trajectory(self.current_position[2], final_points[2], self.current_velocity[2],end_velocity[2],0,0,time, 10)

