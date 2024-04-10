from controller import robot
import numpy as np

class ObstacleDetector:
    def __init__(self, camera, camera_transform, sample_period, lidar=None, lidar_transform=None):
        self.cam = camera #camera transform from webots
        self.camera_width = camera.getWidth()
        self.camera_height = camera.getHeight()
        self.lidar = lidar #lidar object from webots
        self.cam_transform = camera_transform # transformation from robot center to camera frame
        self.lidar_transform = lidar_transform # transformation from robot center to lidar frame

        #metric for noise in the model
        self.noise = 0
        self.accuracy = 0
        self.chance_of_no_detection = 0


        #dictionary for storing different camera objects seen
        self.camera_objects = {}

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
        detected_obstacles = self.cam.getRecognitionObjects()
        for objects in detected_obstacles:
            id = objects.getId()
            #check if we have seen the object before and update position/velocity
            if self.camera_objects.get(id) is not None:
                data = self.camera_objects[id]
                prev_position = data[1] #TODO
                new_position = self.transform_camera_object_position(objects.getPosition())
                self.calc_velocity(prev_position, new_position)
                #make new data for dict and update #TODO
                self.camera_objects.update({id: data})
            else:
                id = objects.getId()
                position = objects.getPosition()
                transformed_position = self.transform_camera_objects(position)
                size = objects.getSize()  # adjust based on size
                velocity = [0,0,0]
                description = objects.getModel()
                relative_location = self.get_relative_location(objects)
                new_data = [id, position, size, velocity, description, relative_location]
                self.camera_objects[id] = new_data

        #prune obstacle list to get rid of old obstacles
        self.prune_obstacles(10, self.robot_position)
        return self.camera_objects.copy()

    #translates lidar point cloud to obstacles in the configuration space.
    def get_lidar_obstacles(self):
        if self.lidar is not None:
            #do something
            return 0
        else:
            return 0

    #helper functions
    def transform_camera_object_position(self, position):
        # transform position
        new_position = np.matmul(self.cam_transform, np.array([position[0], position[1],position[3],1])).reshape(4,1)
        return [new_position[0], new_position[1], new_position[2]]

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

    def calculate_obstacle_velocity(self, prev_position, new_position):
        xv = (new_position[0] - prev_position[0])/self.timestep
        yv = (new_position[1] - prev_position[1])/self.timestep
        zv = (new_position[2] - prev_position[2])/self.timestep
        return [xv,yv,zv]

    def get_relative_location(self, objects, camera_location):
        #for multiple cameras, bin left and right side obstacles to always return their relative location
        if camera_location == "Left Side":
            return "Left"
        elif camera_location == "Right Side":
            return "Right"
        else: #find what side of the image they are on
            camera_location = objects.getPositionOnImage()
            if camera_location[0] <= self.camera_width/2:
                return "Left"
            else:
                return "Right"



