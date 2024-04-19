# this file controls all the obstacle movement in the webots world
import math
from controller import Supervisor
import sys
import time
#
from apf_planner import *
from velocity_obstacle import *
# from obstacle_detector import *

sys.path.insert(0,'E:/capstone_repo/Intuitively-Controlled-Autonomous-System-to-Aid-the-Visually-Impaired/navigation')


obstacle_mover = Supervisor()

time_step = 50
i = 0
k = 0
# initialize all objects to be controlled by the supervisor here and get translation field
ped_2_node = obstacle_mover.getFromDef('Ped_2')
ped_3_node = obstacle_mover.getFromDef('Ped_3')
tesla = obstacle_mover.getFromDef('Tesla')
guide_dog = obstacle_mover.getFromDef('DOG')

ped2_T_field = ped_2_node.getField('translation')
ped3_T_field = ped_3_node.getField('translation')
tesla_T_field = tesla.getField('translation')
dog_T_field = guide_dog.getField('translation')


# initial object positions
ped_2_pos = ped_2_node.getPosition()
ped_3_pos = ped_3_node.getPosition()
tesla_pos = tesla.getPosition()


print(ped_2_pos)

# initialize obstacle speeds
ped_2_vel = .03 # m/ms
ped_3_vel = .04
tesla_speed = .07
switch_flag = 1

# define initial parameters for the robot
dog_pos_init = guide_dog.getPosition()*10          # usually it's around (-15.896,-60.1834)
goal = [-71.2,-30.4,0]*10                  # converting to c-space coordinates


vo_algo = velocityObstacle()
apf_grid_size = [370, 350]                    # make it so that 1 in c-space is .1 in world space or something
o_map = OccupancyMap(740, 700)
distance_tolerance = 1.9
local_planner = APF_Planner(dog_pos_init, goal, apf_grid_size)

robot_velocity = []

while obstacle_mover.step(time_step) != -1:
    # set position changes here
    # define periodic linear trajectory for all objects

    if i%100 == 0:          # this switches the directions for the moving objects
        switch_flag = switch_flag*-1
    ped_2_pos = [switch_flag*ped_2_vel+ped_2_pos[0], ped_2_pos[1], ped_2_pos[2]]
    ped_3_pos = [ped_3_pos[0], switch_flag*ped_3_vel+ ped_3_pos[1], ped_3_pos[2]]
    tesla_pos = [tesla_pos[0], switch_flag*tesla_speed+ tesla_pos[1], tesla_pos[2]]
    ped2_T_field.setSFVec3f(ped_2_pos)
    ped3_T_field.setSFVec3f(ped_3_pos)
    tesla_T_field.setSFVec3f(tesla_pos)

    # initialize obstacle positions
    obstacles = [ped_2_pos[0:1],ped_3_pos[0:1],tesla_pos[0:1]]*10
    o_velocity =[[.3,0],[0,.4],[0,.7]]



    nav_start_time = time.time()
    # this is the velocity obstacle section
    cone_vertices_list = []
    vo_path_list = []
    inflate_radius = 3
    #
    vo_algo.update_obstacles(obstacles, inflate_radius)

    for i in range(len(obstacles)):
        current_cone_vertices = vo_algo.vo_calculation(o_map.occupancy_grid, dog_pos_init, o_velocity[i], robot_velocity)
        cone_vertices_list.append(current_cone_vertices)
        vo_path_list.append(mplpath.Path(current_cone_vertices))
    o_map.discretize_grid(vo_path_list)  # extract mesh of velocity obstacles
    obstacle_coord = o_map.list_of_obstacle_coordinates


    local_planner.repulsive_force(obstacle_coord)  # pass in obstacle coordinates to APF
    local_planner.attractive_force()  # currently has issue with distance calculation
    local_planner.plot_field(obstacle_coord)
    local_path = local_planner.path_finder(distance_tolerance)  # find the path and
    x_path = [coord[0] for coord in local_path]
    y_path = [coord[1] for coord in local_path]
    plt.plot(x_path, y_path, linestyle='-', color='b', label='Coordinates')
    print(local_path)
    nav_end_time = time.time()
    result_time = nav_end_time - nav_start_time

    i+=1
