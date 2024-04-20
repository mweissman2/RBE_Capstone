from controller import robot
import numpy as np
import random

class ObstacleDetector:
    def __init__(self, camera, camera_transform, sample_period, lidar=None, lidar_transform=None):
        self.cam = camera #camera transform from webots
        self.camera_width = camera.getWidth()
        self.camera_height = camera.getHeight()
        self.lidar = lidar #lidar object from webots
        self.cam_transform = camera_transform # transformation from robot center to camera frame
        self.lidar_transform = lidar_transform # transformation from robot center to lidar frame
        self.robot_position = [0,0,0]
        self.camera_location = ''
        #metric for noise in the model
        self.noise = (0.1/3) #3 sigma is 0.1
        self.accuracy = 0.1
        self.chance_of_no_detection = 0.9
        self.time_step = sample_period
        self.max_distance = 20 #meters distance away from obstacle before it is removed from occupancy list


        #dictionary for storing different camera objects seen
        #values are: [id, transformed_position, size, velocity, description, relative_location]
        self.camera_objects = {}

        #set lidar settings
        if self.lidar is not None:
            self.lidar.disablePointCloud()
            self.lidar_fov = self.lidar.getFov()
            self.lidar_layers = self.lidar.getNumberOfLayers()

        #set camera settings
        self.cam.recognitionEnable(sample_period)

    #returns a list of objects with their ID, world location, estimated_radius, estimated_velocity, description, relative location to the robot
    def get_camera_obstacles(self,robot_position):
        self.robot_position = robot_position
        #should pull from an internally set list that is updated occasionally, instead of pulling only when its updated?
        detected_obstacles = self.cam.getRecognitionObjects()
        for objects in detected_obstacles:
            id = objects.getId()
            #check if we have seen the object before and update position/velocity
            if self.camera_objects.get(id) is not None:
                data = self.camera_objects[id]
                prev_position = data[1]
                new_position = self.transform_camera_object_position(objects.getPosition())
                new_size = objects.getSize()[0]
                data[2] = new_size
                data[3] = self.calc_velocity(prev_position, new_position)
                #make new data for dict and update #TODO
                self.camera_objects.update({id: data})
            else:
                # add random chance to not detect obstacle
                if random.random() < self.chance_of_no_detection:
                    id = objects.getId()
                    position = objects.getPosition()
                    transformed_position = self.transform_camera_object_position(position) #add robot position into this as well.
                    size = objects.getSize()[0]  #returns width of object in the camera frame
                    velocity = [0,0,0]
                    description = objects.getModel()
                    relative_location = self.get_relative_location(objects,self.camera_location)
                    new_data = [id, transformed_position, size, velocity, description, relative_location]
                    self.camera_objects[id] = new_data

        #prune obstacle list to get rid of old obstacles
        # self.prune_obstacles(self.max_distance)
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
        #add noise to object position measurement!
        noise_x = random.gauss(0, self.noise)
        noise_y = random.gauss(0, self.noise)
        # transform position
        new_position = np.round(np.matmul(self.cam_transform, np.array([position[0]+noise_x, position[1]+noise_y, position[2], 1])).reshape(4,1),4)
        return [new_position[0]+self.robot_position[0]+self.accuracy, new_position[1]+self.robot_position[1]+self.accuracy, new_position[2]+self.robot_position[2]]

    #need to decide if we are using the point cloud or range image of the class. The range image is faster, and closer to what we would get with a real?
    #but
    def transform_lidar_objects(self, point_cloud):
        #extract lidar FOV and layer parameters
        #convert each pixel of the range image based on the depth ad location within the image
        #does the value reflect x coordinate or angles coordinate
        return 0

    def prune_obstacles(self, distance):
        # iterate through the list of obstacles, and remove if far away from the robot or it is a road
        iterator_list = self.camera_objects.copy()
        for key, value in iterator_list.items():
            if value[4] == 'road' or value[4] == 'crossroad':
                self.camera_objects.pop(key)
            else:
                object_position = value[1]
                dx = (object_position[0]-self.robot_position[0])**2
                dy = (object_position[1]-self.robot_position[0])**2
                total_distance = np.sqrt(dx+dy)
                if total_distance >= distance:
                    removed = self.camera_objects.pop(key)
                    #print('Removed:' + str(removed))

        return 0

    def get_relative_location(self, objects, camera_location):
        #for multiple cameras, bin left and right side obstacles to always return their relative location
        if camera_location == "Left Side":
            return "Left"
        elif camera_location == "Right Side":
            return "Right"
        else: #find what side of the image they are on
            camera_location = objects.getPositionOnImage()
            if camera_location[0] <= self.camera_width/2 * 1.2 and camera_location[0] >= self.camera_width/2 * 0.8:
                return "Front"
            elif camera_location[0] <= self.camera_width/2:
                return "Front Left"
            else:
                return "Front Right"

    def calc_velocity(self,old_position, new_position):
        xvel = np.round(((new_position[0]-old_position[0]) / self.time_step), 3)
        yvel = np.round(((new_position[1]-old_position[1]) / self.time_step), 3)
        zvel = np.round(((new_position[2]-old_position[2]) / self.time_step), 3)

        return [xvel,yvel,zvel]

    def get_camera_context(self):
        camera_context = [[obj[4], obj[5]] for obj in self.camera_objects.values()]
        return camera_context



