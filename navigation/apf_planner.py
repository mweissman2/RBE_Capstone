from typing import Self
from matplotlib import pyplot as plt
import numpy as np
from occupancy_map import *
# notes: https://medium.com/nerd-for-tech/local-path-planning-using-virtual-potential-field-in-python-ec0998f490af

class APF_Planner:
    def __init__(self,start,goal,grid_size,obstacle_list) -> None:
        self.start = start
        self.goal = goal
        self.length = grid_size[0]
        self.width = grid_size[1]

        self.X, self.Y = self.make_grid()
        self.i_vector = np.zeros_like(self.X)
        self.j_vector = np.zeros_like(self.Y)
        
        self.vector_field_dict = {}             # (3,4): [5,6]      [5,6] is 5i + 6j Newtons

        self.force_range = 9
        self.radius = 2
        self.k_att = 5
        self.k_rep = 6
        
    def make_grid(self):
        length_array = np.arange(-self.length//2, self.length//2)
        width_array = np.arange(-self.width//2, self.width//2)
        X, Y = np.meshgrid(length_array, width_array)
        return X, Y
    
    def vector_field_constructor(self):
        for i in self.length:
            for j in self.width:
                pass
                
    
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
                if distance_to_goal > self.radius + self.force_range:     # this tests if you are outside the force-range
                    self.i_vector[i][j] = self.k_att * distance_to_goal * np.cos(theta_goal)
                    self.j_vector[i][j] = self.k_att * distance_to_goal * np.sin(theta_goal)
                else:
                    self.i_vector[i][j] = self.k_att *(distance_to_goal)*np.cos(theta_goal)
                    self.j_vector[i][j] = self.k_att *(distance_to_goal)*np.sin(theta_goal)
                    
    
    def repulsive_force(self):
        pass
        
    def total_force(self):
        pass

    def plot_field(self):
        # Create Vector Field
        fig, ax = plt.subplots(figsize = (self.length,self.width))
        ax.quiver(self.X, self.Y, self.i_vector, self.j_vector)

        # Add goal
        ax.add_patch(plt.Circle(self.goal, 0.5, color='b'))
        ax.annotate("Goal", xy=self.goal, fontsize=10, ha="center")
        ax.set_title('Attractive field of the Goal')
        plt.show() 
     
    def extract_coordinates(self):
        # Plot the streamlines
        stream = plt.streamplot(X, Y, U, V, density=2)

        # Extract the coordinates of the streamlines
        streamlines = stream.lines.get_segments()  # you only need x and y of the 2nd index



start = (0,0)
goal = (0,0)
grid_size = (10,10)
obstacle_list =[[1,5],[2,9],[8,6]]
test_obj = APF_Planner(start, goal, grid_size, obstacle_list)
test_obj.attractive_force()
test_obj.plot_field()

