from controller import robot
import numpy as np

class ObstacleDetector:
    def __init__(self, camera, camera_transform, sample_period, lidar=None, lidar_transform=None):
        self.cam = camera #camera transform from webots
        self.lidar = lidar #lidar object from webots
        self.cam_transform = camera_transform # transformation from robot center to camera frame
        self.lidar_transform = lidar_transform # transformation from robot center to lidar frame

        #metric for noise in the model
        self.noise = 0
        self.accuracy = 0
        self.chance_of_no_detection = 0


        #dictionary for storing different camera objects seen
        self.camera_objects = []

        #set lidar settings
        if self.lidar is not None:
            self.lidar.disablePointCloud()
            self.lidar_fov = self.lidar.getFov()
            self.lidar_layers = self.lidar.getNumberOfLayers()

        #set camera settings
        self.cam.recognitionEnable(sample_period)

    #returns a list of objects with their ID, world location, estimated_radius, estimated_velocity, description, relative location to the robot
    def get_camera_obstacles(self):
        #should pull from an internally set list that is updated occasionally, instead of pulling only when its updated?
        return 0

    #translates lidar point cloud to obstacles in the configuration space.
    def get_lidar_obstacles(self):
        if self.lidar is not None:
            #do something
            return 0
        else:
            return 0

    #helper functions
    def transform_camera_objects(self, camera_objects):
        #get camera objects
        #extract position and update dictionary
        #prune dictionary for obstacles that are far outside of the range of the robot
        return 0

    #need to decide if we are using the point cloud or range image of the class. The range image is faster, and closer to what we would get with a real?
    #but
    def transform_lidar_objects(self, point_cloud):
        #extract lidar FOV and layer parameters
        #convert each pixel of the range image based on the depth ad location within the image
        #does the value reflect x coordinate or angles coordinate
        return 0

    def prune_obstacles(self, distance, robot_position):
        #iterate through the list of obstacles, and remove if far away from the robot.
        return 0

    def calculate_obstacle_velocity(self):
        return 0



