from matplotlib import pyplot as plt
import numpy as np

# notes: https://medium.com/nerd-for-tech/local-path-planning-using-virtual-potential-field-in-python-ec0998f490af

class APF_Planner:
    def __init__(self,start,goal,occupy_map) -> None:
        self.start = start
        self.goal = goal
        self.length = len(occupancy_map)
        self.width = len(occupancy_map[0])
        self.vector_field_dict = {}             # (3,4): [5,6]      [5,6] is 5i + 6j Newtons
        
    
    def vector_field_constructor(self):
        for i in self.length:
            for j in self.width:
                
    
    def attractive_force(self,robot_pose, goal_pos):
        K_att = 5.0  # Gain for attractive force
        theta = np.arctan2((robot_pose[1]-self.goal[1])/(robot_pose[0]-self.goal[0]))
        
    
    
    def repulsive_force(self, robot_pose, obstacle_list):
        pass
        
    def total_force(self):
        pass
        

