from global_planner import *
from velocity_obstacle import *
from occupancy_map import *
import matplotlib.path as mplpath
import matplotlib.pyplot as plt

if __name__ == "__main__":


    # store the ambiguous address/place and send it to places API
    start ="Boston, MA"             # example, it will be current position
    goal = "Worcester, MA"          # comms

    # routes = google_planner(start, goal)  # call google planner and return routes


    # Below is testing
    robot_velocity = [0,5]
    robot_pos = [50,40]
    obstacles = [[50, 60]]             # [x y], needs to be list of lists, might need to convert to dictionary later
    obstacle = obstacles[0]
    o_velocity =[0,-3]


    # print(routes)

    vo_algo = velocityObstacle()

    o_map = OccupancyMap(100,100)
    o_map.test_grid()    # create test grid
    

    vo_algo.update_obstacles(obstacles)
    cone_vertices = vo_algo.vo_calculation(o_map.occupancy_grid,robot_pos,o_velocity,robot_velocity)
    vo_path = mplpath.Path(cone_vertices) # use this to visualize the cone construction
    # only current issue is that the VO triangle seems inverted

    # Extract x and y coordinates from cone_vertices
    x_coords = [vertex[0] for vertex in cone_vertices]
    y_coords = [vertex[1] for vertex in cone_vertices]


    # testing if something is inside the obstacle velocity
    # test_point = (60,42)
    # object_inside = vo_path.contains_point(test_point)

    # if object_inside:
    #     print(f'Point {test_point} is inside the VO')
    # else:
    #     print('Not inside VO')

    o_map.discretize_grid([vo_path])            # eventually need to pass in multiple polygons
    
    # Plot the points
    plt.figure()
    plt.plot(x_coords, y_coords, 'ro')  # 'ro' specifies red circles for points
    plt.plot(*robot_pos,'bo')
    plt.scatter(50,60, color = 'green')
    # Plot the path between vertices
    for i in range(len(cone_vertices)-1):
      plt.plot([cone_vertices[i][0], cone_vertices[i + 1][0]], [cone_vertices[i][1], cone_vertices[i + 1][1]], 'r-')
    plt.plot([cone_vertices[2][0], cone_vertices[0][0]], [cone_vertices[2][1], cone_vertices[0][1]],'r-')   # plot last path
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Visualization of Collision Cone Vertices')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.show()
    

