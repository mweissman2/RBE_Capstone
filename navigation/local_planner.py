# Code for VO and eventually APF implementation
import math

# some notes on VO: https://egreuel.github.io/asv_path_planner/Introduction.html#velocity-obstacle-algorithm


# A* integration with VO: https://www.sciencedirect.com/science/article/pii/S2092678224000050

# import controller       # do i need to pip install?
import numpy as np
import matplotlib.path as mplpath

# steps

# 1) store data from robot and environmental obstacles
    # reduce robot to a point, inflate obstacles by same area as robot
# 2) subtract robot and obstacle velocity vectors to determine relative velocity collision
# 3) create robot frame collision cone through tangent lines
# 4) rotate collision cone by adding each velocity in collision cone with obstacle velocity

# 5) use APF to quickly plan around obstacle

# for testing, we can just use webots omnipresent knowledge of obstacle positions
class velocityObstacle():
    def __init__(self):
        self.obstacles = {}                 # dict of webots world obstacles, key = obstacle id, value = velocity vector
        self.v_obstacles = []               # list to contain velocity obstacles
        self.time_to_collide = 5            # this is an arbitrary buffer value for collision time tolerance
        self.inflation_radius = 9           # avoidance radius around obstacles

        # robot parameters
        self.robot_velocity = []            # pass in current robot velocity vector
        self.robot_pose = []

        # maybe a simple 2D test matrix to represent the world
        self.test_world = np.zeros((80,80), dtype=int)



    def pyth_distance(self,point_1,point_2):
        return math.sqrt((point_1[0]-point_2[0])**2+(point_1[1]-point_2[1])**2)

    def collision_cone(self,local_occupy_map,robot_pos,t_1,t_2,velocity_of_obstacle,robo_velocity):
        # calculate collision cone for incoming obstacles
        # probably needs to be called at some high frequency
        '''
        local_occupy_map is the matrix that will contain the obstacles surrounding the robot
        t_1 and t_2 are the tangent points connected to the
        '''
        t = 6           # this establishes 6 second future horizon window
        new_t1 = [t_1[0] + velocity_of_obstacle[0]*t,t_1[1] + velocity_of_obstacle[1]*t]
        new_t2 = [t_2[0] + velocity_of_obstacle[0]*t,t_2[1] + velocity_of_obstacle[1]*t]
        new_apex_point = [(robo_velocity[0] - velocity_of_obstacle[0])*t+robot_pos[0],(robo_velocity[0] - velocity_of_obstacle[0])*t+robot_pos[0]]      # the apex point of the obstacle would be vector shift of robot position by velocity of object minus distance covered from difference of obstacle and robot velocities.
        cone_vertices = np.array([new_apex_point,new_t1,new_t2])

        return cone_vertices


        # this line is used to test if points are inside a triangle
        # inside_triangle = path.contains_points(points)



    def tangent_calc(self,obstacle,robot_position):
        # https://math.stackexchange.com/questions/543496/how-to-find-the-equation-of-a-line-tangent-to-a-circle-that-passes-through-a-g

        dx, dy = robot_position[0] - obstacle[0], robot_position[1] - obstacle[1]
        dxr, dyr = -dy, dx
        distance = self.pyth_distance(self.robot_pose, obstacle)

        if distance >=self.inflation_radius:
            rho = self.inflation_radius/distance
            ad = rho**2
            bd = rho*math.sqrt(1-rho**2)
            # calculate tangent points
            tangent_1 = [obstacle[0] + ad * dx + bd * dxr, obstacle[1] + ad * dy + bd * dyr]
            tangent_2 = [obstacle[0] + ad * dx - bd * dxr, obstacle[1] + ad * dy - bd * dyr]
            return tangent_1,tangent_2

        else:
            # if distance to center of obstacle is less than radius, then obstacle space has been breached
            # send emergency stop command to robot
            pass



    def vo_calculation(self,local_occupy_map,robot_pos,velocity_of_obstacle,robot_velocity):
        # calculate the velocity obstacle from obstacles
        cone_coordinates = []
        self.robot_pose = robot_pos
        for obstacle in self.obstacles:
                        # obtain v prime vector, which velocity component from robot towards obstacle
            # create tangent lines from robot to inflated obstacle

            # find distance from point to obstacle center
                   # pass in robot and obstacle position
            t1, t2 = self.tangent_calc(obstacle, self.robot_pose)
            cone_coordinates = self.collision_cone(local_occupy_map,robot_pos,t1,t2,velocity_of_obstacle,robot_velocity)
        return cone_coordinates

        # create

    def update_obstacles(self,new_obstacles):
        self.obstacles = new_obstacles  # dict of webots world obstacles, key = obstacle id, value = velocity vector

    def obstacle_inflation(self):
        # here the obstacle needs to be inflated according to the dimensions of the robot
        # creating an inflated circle around obstacle is the easiest
        pass

    def detect(self):
        # detect whether the robot will enter the velocity obstacle space
        pass

    def trajectory_plan(self):
        # given the obstacles created from VO, plan a path around
        pass