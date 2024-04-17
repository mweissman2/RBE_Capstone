import math

from matplotlib import pyplot as plt
import numpy as np
from occupancy_map import *
# notes: https://medium.com/nerd-for-tech/local-path-planning-using-virtual-potential-field-in-python-ec0998f490af

class APF_Planner:
    def __init__(self,start,goal,grid_size) -> None:
        self.start = start
        self.goal = goal
        self.length = grid_size[0]
        self.width = grid_size[1]

        self.X, self.Y = self.make_grid()           # define X and Y containers using grid_function
        self.i_vector = np.zeros_like(self.X)
        self.j_vector = np.zeros_like(self.Y)

        self.force_range = 5
        self.goal_radius = 2
        self.obstacle_radius = 1
        self.k_att = 4
        self.k_rep = -4
             # store the coordinates of all obstacles in here


    def make_grid(self):
        length_array = np.arange(-self.length//2, self.length//2)
        width_array = np.arange(-self.width//2, self.width//2)
        X, Y = np.meshgrid(length_array, width_array)
        return X, Y
    def reset_vectors(self):
        # simply resets i,j vectors for whole field, this assumes workspace is always the same, can use arguments to change it
        self.i_vector = np.zeros_like(self.X)
        self.j_vector = np.zeros_like(self.Y)

    
    def attractive_force(self):
        '''
        Produces attractive force vector field based on goal
        '''
        for i in range(self.length):
            for j in range(self.width):
                distance_to_goal = np.sqrt((self.X[i][j]-self.goal[0])**2 + (self.Y[i][j]-self.goal[1])**2)

                theta_goal= np.arctan2(self.goal[1] - self.Y[i][j], self.goal[0]  - self.X[i][j])
                
                #if distance_to_goal < self.radius:
                    #self.i_vector[i][j] = 0
                    #self.j_vector[i][j] = 0
                if distance_to_goal > self.goal_radius + self.force_range:     # this tests if you are outside the force-range
                    if self.i_vector[i][j] != 0:
                        self.i_vector[i][j] += self.k_att * distance_to_goal * np.cos(theta_goal)
                        self.j_vector[i][j] += self.k_att * distance_to_goal * np.sin(theta_goal)
                    else:
                        self.i_vector[i][j] += self.k_att * distance_to_goal * np.cos(theta_goal)
                        self.j_vector[i][j] += self.k_att * distance_to_goal * np.sin(theta_goal)
                else:
                    if self.i_vector[i][j] != 0:
                        self.i_vector[i][j] += self.k_att *(distance_to_goal)*np.cos(theta_goal)
                        self.j_vector[i][j] += self.k_att *(distance_to_goal)*np.sin(theta_goal)
                    else:
                        self.i_vector[i][j] += self.k_att * (distance_to_goal) * np.cos(theta_goal)
                        self.j_vector[i][j] += self.k_att * (distance_to_goal) * np.sin(theta_goal)
                    
    
    def repulsive_force(self,obstacles):
        # first iterate through all obstacles
        for obs in obstacles:
            for i in range(self.length):
                for j in range(self.width):
                    distance_to_obs = np.sqrt((obs[0] - self.X[i][j]) ** 2 + (obs[1] - self.Y[i][j]) ** 2)
                    theta_obstacle = np.arctan2(obs[1] - self.Y[i][j], obs[0] - self.X[i][j])

                    if distance_to_obs < self.obstacle_radius:
                        self.i_vector[i][j] += np.sign(np.cos(theta_obstacle))
                        self.j_vector[i][j] += np.sign(np.sin(theta_obstacle))
                    elif distance_to_obs > self.obstacle_radius + self.force_range:
                        self.i_vector[i][j] += 0
                        self.j_vector[i][j] += 0
                    elif distance_to_obs < self.obstacle_radius + self.force_range:
                        self.i_vector[i][j] += 2*self.k_rep*(self.obstacle_radius+self.force_range-distance_to_obs)*np.cos(theta_obstacle)
                        self.j_vector[i][j] += 2*self.k_rep*(self.obstacle_radius+self.force_range-distance_to_obs)*np.sin(theta_obstacle)

        

    def plot_field(self,obstacles):
        # Create Vector Field
        fig, ax = plt.subplots(figsize = (10,10))
        ax.quiver(self.X, self.Y, self.i_vector, self.j_vector)

        # Add goal
        ax.add_patch(plt.Circle(self.goal, 0.5, color='b'))
        ax.annotate("Goal", xy=self.goal, fontsize=10, ha="center")
        for obs in obstacles:
            # plot all the obstacles
            ax.add_patch(plt.Circle(obs, 0.5, color='r'))
            ax.annotate(f"Obstacle {obs}", xy = obs,fontsize=10, ha = "center")
        ax.set_title('vector field of Goal and Obstacles')
        # self.stream_path = plt.streamplot(self.X, self.Y, self.i_vector, self.j_vector, start_points = np.array(self.start).reshape(1,2),density = 1)


    def get_next_point(self,current_pose):

        column_x = np.where(self.X == current_pose[0])[1][0]
        corresponding_y_values = self.Y[:, column_x]
        row_y = np.where(corresponding_y_values == current_pose[1])[0][0]

        local_i_vec = self.i_vector[row_y][column_x]
        local_j_vec = self.j_vector[row_y][column_x]
        # calculate angle from the unit vector
        angle_to_approach = math.atan2(local_j_vec,local_i_vec)
        degree_threshold_22 = math.pi/8             # named after pi/8 which is about 22.5 degrees
        # iterate through all direction permutations, mutually exclusive
        if math.pi/2 + degree_threshold_22 > angle_to_approach > math.pi/2 - degree_threshold_22:   # north
            next_point = [current_pose[0],current_pose[1]+1]
        elif math.pi/2 - degree_threshold_22 >= angle_to_approach >= degree_threshold_22:           # northeast
            next_point = [current_pose[0]+1, current_pose[1] + 1]
        elif degree_threshold_22 > angle_to_approach > -degree_threshold_22:                        # east
            next_point = [current_pose[0]+1, current_pose[1]]
        elif -degree_threshold_22 >= angle_to_approach >= -math.pi/2+degree_threshold_22:                    # southeast
            next_point = [current_pose[0] + 1, current_pose[1]-1]
        elif -math.pi/2+degree_threshold_22 > angle_to_approach > -math.pi/2 - degree_threshold_22:     # south
            next_point = [current_pose[0], current_pose[1]-1]
        elif -math.pi/2-degree_threshold_22 >= angle_to_approach >= -math.pi + degree_threshold_22:     # southwest
            next_point = [current_pose[0]-1, current_pose[1]-1]
        elif -math.pi + degree_threshold_22 > angle_to_approach >= -math.pi or math.pi - degree_threshold_22 < angle_to_approach <= math.pi:     # west
            next_point = [current_pose[0]-1, current_pose[1]]
        elif math.pi - degree_threshold_22 >= angle_to_approach >= math.pi/2 + degree_threshold_22:    # northwest
            next_point = [current_pose[0] - 1, current_pose[1] + 1]

        return next_point

    def get_distance(self,first_point,second_point):
        distance = math.sqrt((first_point[0]-second_point[0])**2+(first_point[1]-second_point[1])**2)
        return distance

    def path_finder(self,distance_tolerance):
        # exploring each node, build path based on arrow direction
        # mini search

        path = []
        next_node = self.get_next_point(self.start)
        path.append(next_node)
        for i in range(1000):
            next_node = self.get_next_point(next_node)
            path.append(next_node)

            if self.get_distance(next_node,self.goal) <= distance_tolerance:  #maybe just make this
                return path



        # Extract the coordinates of the streamlines
        # streamlines = self.stream_path.lines.get_segments()  # you only need x and y of the 2nd index
        # return [pt[1] for pt in streamlines]



# test case
# start = (0,5)
# goal = (0,0)
# grid_size = (30,30)
# # obstacle_list =[[1,5],[2,9],[8,6]]
# obstacle_list =[[12,5],[-2,-9]]
# test_obj = APF_Planner(start, goal, grid_size, obstacle_list)
#
# test_obj.repulsive_force(obstacle_list)
# test_obj.attractive_force()
# test_obj.plot_field(obstacle_list)
#
# path = test_obj.extract_coordinates()
# print([path])
# for coord in path:
#     if abs(coord[0]-start[0]) < .0001 and abs(coord[1]-start[1]) < .0001:
#         print(f'Closest start point is: {coord}')
#         new_start = coord
#
# plt.show()

