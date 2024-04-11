#init code here is not proper
from robot_motion_controller import motion_controller
from velocity_obstacle import *

comms = communcation_controller()
user_tracker = Gimbal_Controller()
motion = Motion_Controller()
front_sensors = Object_Detector()
local_planner = Local_Planner_Controller()

velocity_target = 0.7 #m/s
velocity_max = 1.4
velocity_min = 0
velocity_delta = 0.3

counter = 0

# instantiate necessary objects
vo_algo = velocityObstacle()
local_start = [10, -20]
local_goal = [0, 10]
grid_size = [50, 50]

local_planner = APF_Planner(local_start, local_goal, grid_size)


while robot.step(timestep) != -1:

    #check comms flags?
    #start navigation
    if comms.navigation_flag:
        #visualize global plan or
        #send first waypoint to local Planner
        comms.reset_navigation_flag()


    #change speed flag should be between -1 to 1. zero means no update
    if comms.change_speed_flag == 1:
        velocity_target += velocity_delta
        if velocity_target > velocity_max:
            velocity_target = velocity_max
        comms.reset_change_speed_flag
    elif comms.change_speed_flag == -1:
        velocity_target -= velocity_delta
        if velocity_target < velocity_min:
            velocity_target = velocity_min
        comms.reset_change_speed_flag

    #simulator has run 200 ms so run those steps
    if counter%200 == 0:
        #run user tracking and obstacle detection before local planner
        user_position, out_of_range_flag = user_tracker.run()
        #finds obstacles
        obstacles = front_sensors.get_camera_obstacles()
        #local planner takes in obstacles and caculates the next point to send to the motion planner
        vo_algo.update_obstacles(obstacles)
        for i in range(len(obstacles)):
            current_cone_vertices = vo_algo.vo_calculation(o_map.occupancy_grid, robot_pos, o_velocity[i],
                                                           robot_velocity)
            cone_vertices_list.append(current_cone_vertices)
            vo_path_list.append(mplpath.Path(current_cone_vertices))  # use this to visualize the cone construction
        local_planner.repulsive_force(obstacle_coord)  # pass in obstacle coordinates to APF
        local_planner.attractive_force()  # currently has issue with distance calculation
        # local_planner.plot_field(obstacle_coord)
        local_planner.extract_points        # must add extractor method to this

        #when it recieves a new point it makes a new trajectory
        motion_controller.calc_trajectory(next_waypoint,next_velocity)

    #if the user wants to move forward, and they are not out of range, the send motion control
    if comms.go_flag and not out_of_range_flag:
        #normally the motion planner runs next next step
        motion_controller.send_next_step(next_velocity)
    else: #else don't do anything
        motion_controller.stop()
        #maybe send something to comms class.


    counter += timestep

    pass