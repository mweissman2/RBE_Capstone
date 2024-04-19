

from re import L
import numpy as np
import matplotlib.path as mplpath
from matplotlib import pyplot as plt

class OccupancyMap:

    def __init__(self, length, width):
        self.occupancy_grid = []
        self.length = length
        self.width = width
        self.occupancy_grid = np.zeros((self.length,self.width),dtype = int)
        #self.verteces = verteces
        self.list_of_obstacle_coordinates = []


    def test_grid(self):
        # create test array for obstacle velocity
        self.length = 20
        self.width = 20 
        self.occupancy_grid = np.zeros((self.length,self.width),dtype = int)
        self.occupancy_grid[4][5],self.occupancy_grid[6][7], self.occupancy_grid[1][3] = 1


        # put some random obtacles in it
    def discretize_grid(self,obstacle_paths):
        # Pass in list of obstacle polygon paths
        
        # test every point in grid for occupancy and populate values 
        # 0 is free space and 1 is occupied 
        for i in range(0,self.width):
            for k in range(0,self.length):
                for polygon in obstacle_paths:
                    object_detected = polygon.contains_point([i,k])
                    if object_detected:
                        self.occupancy_grid[i][k] = 1
                        # print(f'Point {[i,k]} is inside the VO')
                        self.list_of_obstacle_coordinates.append([i,k])
                    else:
                        self.occupancy_grid[i][k] = 0
                        # print('Not inside VO')
        plt.figure()
        plt.imshow(self.occupancy_grid, origin='lower')
        #for i in range(0,self.width):
         #   for k in range(0,self.length):
          #      if self.occupancy_grid[i][k] == 1:
           #         plt.plot(i, k)
        # plt.show()



# v1 = np.array([1,1])
# v2 = np.array([3,3])
# test_verteces = [v1, v2]
# test = OccupancyMap(5,5,)
# test.discretize_grid()