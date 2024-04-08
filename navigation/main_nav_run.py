from global_planner import *
from velocity_obstacle import *
from occupancy_map import *
from apf_planner import *
import matplotlib.path as mplpath
import matplotlib.pyplot as plt


if __name__ == "__main__":


    # store the ambiguous address/place and send it to places API
    global_start ="Boston, MA"             # example, it will be current position
    global_goal = "Worcester, MA"          # comms

    # routes = google_planner(global_start,   global_goal )  # call google planner and return routes


    # Below is testing
    robot_velocity = [0,5]
    robot_pos = [-30,40]
    robot_goal = [0,0]
    obstacles = [[10, 10],[-10,5],[6,12]]             # [x y], needs to be list of lists, might need to convert to dictionary later
    obstacle = obstacles[0]
    o_velocity =[[0,-3],[1,2],[.5,-.5]]


    # print(routes)
    cone_vertices_list = []
    vo_path_list = []


    vo_algo = velocityObstacle()

    o_map = OccupancyMap(100,100)
    # o_map.test_grid()    # create test grid
    
    # add computational time data
    vo_algo.update_obstacles(obstacles)
    for i in range(len(obstacles)):
        current_cone_vertices = vo_algo.vo_calculation(o_map.occupancy_grid, robot_pos, o_velocity[i], robot_velocity)
        cone_vertices_list.append(current_cone_vertices)
        vo_path_list.append(mplpath.Path(current_cone_vertices))                  # use this to visualize the cone construction


    # Extract x and y coordinates from cone_vertices
    x_coords = [vertex[0] for vertex in cone_vertices_list]
    y_coords = [vertex[1] for vertex in cone_vertices_list]


    o_map.discretize_grid(vo_path_list)           # extract mesh of velocity obstacles
    obstacle_coord = o_map.list_of_obstacle_coordinates
    # APF section

    local_start = [10, -20]
    local_goal = [0, 10]
    grid_size = [50, 50]

    local_planner = APF_Planner(local_start, local_goal, grid_size)

    local_planner.repulsive_force(obstacle_coord)       # pass in obstacle coordinates to APF
    local_planner.attractive_force()            # currently has issue with distance calculation
    local_planner.plot_field(obstacle_coord)
    # Plot the points
    # plt.figure()
    # plt.plot(x_coords, y_coords, 'ro')  # 'ro' specifies red circles for points
    # plt.plot(*robot_pos,'bo')
    # plt.scatter(50,60, color = 'green')
    # # Plot the path between vertices
    # for i in range(len(cone_vertices_list) - 1):
    #   plt.plot([cone_vertices_list[i][0], cone_vertices_list[i + 1][0]], [cone_vertices_list[i][1], cone_vertices_list[i + 1][1]], 'r-')
    # plt.plot([cone_vertices_list[2][0], cone_vertices_list[0][0]], [cone_vertices_list[2][1], cone_vertices_list[0][1]], 'r-')   # plot last path
    # plt.xlabel('X')
    # plt.ylabel('Y')
    # plt.title('Visualization of Collision Cone Vertices')
    # plt.gca().set_aspect('equal', adjustable='box')
    # plt.grid(True)
    plt.show()
    
    # matplotlib.use('TkAgg') # separate window for visualization
