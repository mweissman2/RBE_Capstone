from controller import robot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')

data_len = 200

class Motion_Controller:
    def __init__(self, wheel1, wheel2, wheel3, wheel4, localization, heading):
        self.inside_wheel_front = wheel1 #front left
        self.inside_wheel_back = wheel4 #back right
        self.outside_wheel_front = wheel2 #front right
        self.outside_wheel_back = wheel3 #back left
        self.localization = localization
        self.heading = heading

        self.time_steps = 4
        self.current_position = [0,0,0]
        self.current_velocity = [0,0,0]
        self.goal_position = [0,0,0]
        self.error_epsilon = 0.4
        self.heading_epsilon = 0.3
        self.current_heading = 0
        self.wheel_radius = 0.125
        self.l_x = 0.2
        self.l_y = 0.2
        self.curr_time = 0
        self.goal_time = 0

        self.x_array = []
        self.y_array = []
        self.x_goal = []
        self.y_goal = []

        self.x_vel_traj = []
        self.y_vel_traj = []
        self.z_vel_traj = []
        self.time_interval = 0
        self.x_positions = []
        self.y_positions = []
        self.z_positions = []
        self.trajectory_index = 0
        self.max_index = 0
        self.turn_first = False #flag set if there is a big heading change, and the robot needs to turn first

        #self.fig, (self.ax1, self.ax2) = plt.subplots(2,1)
        #self.line, = self.ax.plot(list(range(0,200)), [0]*200)

        self.finished_flag = False

    #input array is [vx,vy,wz]
    def set_velocity(self, vx, vy, wz):
        #print([vx, vy, wz])
        wheel_velocities = self.inverse_kinematics(vx, vy, wz)

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

    def get_heading(self):
        return self.current_heading

    def set_heading(self, new_heading):
        self.current_heading = new_heading

    def get_encoder_reading(self, wheel):
        return 0

    #internal check true if providing position from outside sources
    def set_current_position(self, robot_position, internal_check):
        if internal_check:
            pose = [robot_position[0], robot_position[1]]
        else:
            pose = self.localization.getValues()
        heading = self.heading.getRollPitchYaw()
        self.current_position = [pose[0], pose[1], heading[2]]

    def send_next_step(self, velocity_goal, robot_position):
        self.set_current_position(robot_position, True)
        if self.finished_flag == False:
            print(self.trajectory_index)

            if abs(self.current_position[0] - self.x_positions[self.trajectory_index]) <= self.error_epsilon:
                if abs(self.current_position[1] - self.y_positions[self.trajectory_index]) <= self.error_epsilon:
                    if abs(self.current_position[2] - self.z_positions[self.trajectory_index]) <= self.heading_epsilon:  # heading error is less important
                        self.trajectory_index += 1
                        if self.trajectory_index >= self.max_index:
                            self.trajectory_index -= 1
                            print("At Goal")
                            self.at_goal_position()
                            return False

            x_vel_setpoint = self.calc_velocity_setpoint(self.current_position[0], self.x_positions[self.trajectory_index], self.time_interval, 20)
            y_vel_setpoint = self.calc_velocity_setpoint(self.current_position[1], self.y_positions[self.trajectory_index], self.time_interval, 20)
            z_vel_setpoint = self.calc_velocity_setpoint(self.current_position[2], self.z_positions[self.trajectory_index], self.time_interval, 20)

            #normalize vectors
            mag = np.sqrt(x_vel_setpoint ** 2 + y_vel_setpoint ** 2)

            # set new velocity values
            x_vel_setpoint = velocity_goal * (x_vel_setpoint / mag)
            y_vel_setpoint = velocity_goal * (y_vel_setpoint / mag)

            self.set_velocity(x_vel_setpoint, y_vel_setpoint,z_vel_setpoint)
            return True
        else:
            print("need new trajectory")
            return False

    def at_goal_position(self):
        self.finished_flag = True
        self.set_velocity(0,0,0)

        return False

    def inverse_kinematics(self, x_vel, y_vel, z_vel):
        inv_kin = np.array([[1, -1, -(self.l_x+self.l_y)],
                            [1, 1, (self.l_x+self.l_y)],
                            [1, 1, -(self.l_x+self.l_y)],
                            [1, -1, (self.l_x+self.l_y)]], dtype=np.float64) / self.wheel_radius

        vels = np.array([x_vel, y_vel, z_vel]).reshape(3,1)
        [wfl, wfr, wbl, wbr] = np.matmul(inv_kin, vels)
        return [wfl, wfr, wbl, wbr]


    def quintic_trajectory(self, x_i, x_f, xd_i, xd_f, xdd_i, xdd_f, t, steps):
        inputs = np.array([x_i, x_f, xd_i, xd_f, xdd_i, xdd_f]).reshape(6,1)

        matrix = np.array([[0,0,0,0,0,1],
                           [np.power(t,5), np.power(t,4), np.power(t,3), np.power(t,2), t, 1],
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

    def plan_trajectory(self, final_points, end_velocities, time):
        self.set_current_position()
        [self.x_positions, self.x_vel_traj, xdd_traj] = self.quintic_trajectory(self.current_position[0], final_points[0], self.current_velocity[0],end_velocities[0],0,0,time, self.time_steps)
        [self.y_positions, self.y_vel_traj, ydd_traj] = self.quintic_trajectory(self.current_position[1], final_points[1], self.current_velocity[1],end_velocities[1],0,0,time, self.time_steps)
        [self.z_positions, self.z_vel_traj, wdd_traj] = self.quintic_trajectory(self.current_position[2], final_points[2], self.current_velocity[2],end_velocities[2],0,0,time, self.time_steps)
        #reset trajectory status flags
       # time = np.linspace(0,time, self.time_steps)
        self.time_interval = time/self.time_steps
        self.finished_flag = False
        self.trajectory_index = 1
        self.max_index = len(self.x_positions)

    def plot(self):
        self.x_array.append(self.current_position[0])
        #self.x_array = self.x_array[-200:]
        self.y_array.append(self.current_position[1])
        #self.y_array = self.y_array[-200:]
        # print('Goal')
        self.x_goal.append(self.x_positions[self.trajectory_index])
        #self.x_goal = self.x_goal[-200:]
        self.y_goal.append(self.y_positions[self.trajectory_index])
        #self.y_goal = self.y_goal[-200:]
        # self.line.set_data(self.x_array, self.y_array)
        self.ax1.plot(self.y_goal)
        self.ax1.plot(self.y_array)
        self.ax2.plot(self.x_array)
        self.ax2.plot(self.x_goal)
        self.ax2.set_ylabel('X_position')
        self.ax1.set_ylabel('Y_position')
        self.ax1.set_title('Robot Position vs Setpoint')
        #self.ax1.set_xlim([-5, 5])
        #self.ax1.set_ylim([-5, 5])
        plt.show(block=False)
        plt.pause(0.001)

    def calc_velocity_setpoint(self, current_position, set_position, time_interval, saturation):
        current_velocity = (set_position - current_position) / time_interval
        if current_velocity > saturation:
            current_velocity = saturation

        return current_velocity

    #calculates needed velocities to go to next point given
    def new_plan_trajectory(self, goal_position, time, curr_time):
        self.curr_time = curr_time
        self.goal_time = curr_time+time

        #transform world coordinate to robot frame.
        angle = self.current_position[2]
        x = self.current_position[0]
        y = self.current_position[1]
        tf_matrix = np.array([[np.cos(angle), np.sin(angle),0, -x*np.cos(angle)-y*np.sin(angle)],
                              [-np.sin(angle), np.cos(angle),0, x*np.sin(angle)-y*np.cos(angle)],
                              [0,0,-1,-np.cos(angle)],
                              [0,0,0,1]])

        res = np.matmul(tf_matrix, np.array([goal_position[0], goal_position[1],0,1]).reshape(4,1)).reshape(4)
        x_delta = res[0]
        y_delta = res[1]
        heading_delta = goal_position[2] - self.current_position[2]
        #heading_delta = 0
        #x_delta = goal_position[0] - self.current_position[0]
        #y_delta = goal_position[1] - self.current_position[1]

        if abs(heading_delta) < 0.05:
            angular_velocity = 0
            velocities = np.array([x_delta/time, y_delta/time]).reshape(2,1)
        else:
            if heading_delta > np.pi:
                heading_delta = heading_delta - 2*np.pi
            elif heading_delta < -np.pi:
                heading_delta = heading_delta + 2*np.pi

            angular_velocity = heading_delta / time

            m11 = (np.sin(angular_velocity*time))/angular_velocity
            m12 = (np.cos(angular_velocity*time))/angular_velocity - (1/angular_velocity)
            m21= -(np.cos(angular_velocity * time)) / angular_velocity + (1/angular_velocity)
            m22 = (np.sin(angular_velocity*time))/angular_velocity


            xm = x_delta
            ym = y_delta

            velocities = np.matmul(np.linalg.inv(np.array([[m11, m12],[m21, m22]])), np.array([xm, ym]).reshape(2,1))
            #print(velocities)
        self.goal_position = goal_position

        self.x_vel_traj = velocities[0][0]
        self.y_vel_traj = velocities[1][0]
        self.z_vel_traj = angular_velocity

    def move(self, curr_time, robot_position):
        self.set_current_position(robot_position, True)
        self.curr_time = curr_time
        #print(self.current_position)

        if not self.finished_flag:

            if self.curr_time > self.goal_time+0.5:
                print("missed the target")
                if abs(self.current_position[0] - self.goal_position[0]) <= self.error_epsilon*5:
                    if abs(self.current_position[1] - self.goal_position[1]) <= self.error_epsilon*5:
                        print("Close to Goal")
                        self.at_goal_position() #TODO
                        #return False

            else:
                if abs(self.current_position[0] - self.goal_position[0]) <= self.error_epsilon:
                    if abs(self.current_position[1] - self.goal_position[1]) <= self.error_epsilon:
                        if abs(self.current_position[2] - self.goal_position[2]) <= self.heading_epsilon:  # heading error is less important
                            print("At Goal")
                            self.at_goal_position()
                            #return False
                else:
                    self.set_velocity(self.x_vel_traj, self.y_vel_traj, self.z_vel_traj)

        return self.finished_flag

