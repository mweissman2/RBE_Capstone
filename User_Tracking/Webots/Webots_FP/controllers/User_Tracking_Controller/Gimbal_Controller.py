import math

from controller import robot
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from controller import CameraRecognitionObject
#class for gimbal that can be instantiated multiple times
class Gimbal_Controller:
    def __init__(self, rgb_camera, depth_camera, gimbal_joints, update_time):
        #set references to simulation objects
        self.rgb_camera = rgb_camera
        self.depth_camera = depth_camera
        self.yaw_axis_motor = gimbal_joints[0]
        self.pitch_axis_motor = gimbal_joints[1]
        self.motor_update_time = 32
        self.horizontal_fov = self.rgb_camera.getFov()

        #extract camera parameters
        self.cam_horizontal_res = float(self.rgb_camera.getWidth())
        self.cam_vertical_res = float(self.rgb_camera.getHeight())

        #define starting poisition of gimbal
        self.starting_yaw_axis_angle = 0
        self.starting_pitch_axis_angle = 0

        #define set point for user tracking, normalized
        self.x_setpoint = float(self.cam_horizontal_res/2)
        self.y_setpoint = float(self.cam_vertical_res/2)

        #saves state of last main direction to rotate that way if person is lost.
        self.last_direction = 1 #positive 1 for positive rotation, -1 for negative rotation
        self.user_in_frame = False
        self.tracking_flag = False
        self.use_estimator = False
        #self.center_error_margin = 0.06 #50 pixels?
        self.center_error_margin = 0.2
        self.max_distance = 3 #max distance the user is allowed to be from the robot

        self.x_velocity_buffer = [0,0,0,0,0]
        self.y_velocity_buffer = [0,0,0,0,0]
        self.velocity_buffer_index = 0
        self.prev_position = [-2,0]
        self.estimated_position = [0,0]
        self.next_position = [0,0]
        self.prev_velocity = [0,0]

        self.current_yaw_axis_angle = 0
        self.current_pitch_axis_angle = 0
        self.yaw_pid = [0.45, 0.03, 0]
        self.yaw_pid_errors = [0,0] #last error, error sum
        self.pitch_pid = [0.35 , 0, 0]
        self.pitch_pid_errors = [0, 0]  #last error, error sum
        self.update_time = update_time
        self.user_id = 30
        self.red_thresh = 64
        self.green_thresh = 140
        self.blue_thresh = 51


    #function which represents finding the user in an initial setup
    def set_user_id(self, user_id):
        self.user_id = user_id

    #runs the PID loop to move the gimbal module to center the user in the frame and the measures their position
    def center_user(self, user_position_in_image, good_frame):
        #normalize inputs
        x_input = (float(user_position_in_image[0])/self.cam_horizontal_res) - 0.5
        y_input = (float(user_position_in_image[1])/self.cam_vertical_res) - 0.5
        #normalize setpoints
        xn_setpoint = (self.x_setpoint/self.cam_horizontal_res) - 0.5
        yn_setpoint = (self.y_setpoint / self.cam_vertical_res) - 0.5


        yaw_pos_diff, self.yaw_pid_errors[0], self.yaw_pid_errors[1] = self.calc_pid(xn_setpoint, x_input, self.yaw_pid, self.yaw_pid_errors[0], self.yaw_pid_errors[1])
        self.yaw_axis_motor.setPosition(self.current_yaw_axis_angle+yaw_pos_diff)
        pitch_pos_diff, self.pitch_pid_errors[0], self.pitch_pid_errors[1] = self.calc_pid(yn_setpoint, y_input, self.pitch_pid, self.pitch_pid_errors[0], self.pitch_pid_errors[1])
        self.pitch_axis_motor.setPosition(self.current_pitch_axis_angle-pitch_pos_diff)


        #determine last direction
        if pitch_pos_diff > 0:
            self.last_direction = -1
        else:
            self.last_direction = 1
        #if within an error threshold for image centering, #then calculate depth and angle
        if np.abs(xn_setpoint-x_input) < self.center_error_margin:
            user_location = self.get_user_location(good_frame,[x_input, y_input])
        else:
            user_location = self.estimate_next_position(self.prev_position, self.prev_velocity)




    #calculates the depth and angle and calculates the user position
    def get_user_location(self, good_frame, position_on_image):
        #calculate depth
        depth = self.calculate_depth(good_frame)
        #calculate angle
        angle = self.calculate_angle()
        #calculate position from robot
        curr_position = self.calculate_user_position_new(depth, angle, position_on_image)
        #update velocity estimator
        curr_velocity = self.interpolate_velocity(curr_position)
        #update state estimator
        self.estimated_position = (np.array(self.prev_position) + np.array(self.next_position)) / 2.0

        self.estimate_next_position(curr_position,curr_velocity)

        return (curr_position, curr_velocity)


    #coarse function for finding the user within world if they are not in frame
    def find_user(self):
        self.update_sensor_readings()
        good_frame = []
        objects = self.rgb_camera.getRecognitionObjects()
        #assumes the user is not in Frame
        self.user_in_frame = False
        for obj in objects:
            if obj.getId() == self.user_id:
                #if they are found then set boolean to true
                self.user_in_frame = True
                self.tracking_flag = True
                position = obj.getPosition()
                position_on_image = obj.getPositionOnImage()
                #TODO maybe change to just sending the image, or the segmentation?
                my_frame = self.rgb_camera.getImageArray()
                good_frame = my_frame.copy()

        if self.user_in_frame == True:
            #call the center user function
            self.center_user(position_on_image, good_frame)
        else:
            #else do continuous rotation in the same as the previous direction to find user
            #calculate new angle and set
            self.tracking_flag = False
            new_angle = self.current_yaw_axis_angle + (self.last_direction*0.35)
            self.yaw_axis_motor.setPosition(new_angle)

    #function for applying mask to image for depth measurement
    def segment_image(self, image):
        #remove infinity from array
        image[image > 100] = 0
        #img = np.frombuffer(self.rgb_camera.getImage(), dtype=np.uint8).reshape((self.rgb_camera.getHeight(), self.rgb_camera.getWidth(), 4))
        img_seg = np.frombuffer(self.rgb_camera.getRecognitionSegmentationImage(), dtype=np.uint8).reshape((self.rgb_camera.getHeight(), self.rgb_camera.getWidth(), 4))
        #separate into colors
        blue = img_seg[:,:,0]
        green = img_seg[:,:,1]
        red = img_seg[:,:,2]

        #set proper thresholds for mask color
        red_mask = cv.inRange(red, self.red_thresh-1, self.red_thresh+1)
        green_mask = cv.inRange(green, self.green_thresh-1, self.green_thresh+1)
        blue_mask = cv.inRange(blue, self.blue_thresh-1, self.blue_thresh+1)

        #new mask based on specified color thresholding
        red_green_mask = cv.bitwise_and(red_mask, green_mask)
        all_mask = cv.bitwise_and(red_green_mask, blue_mask)

        #img_gray = cv.cvtColor(img_seg, cv.COLOR_BGRA2GRAY)
        #ret, img_mask = cv.threshold(img_gray,30, 255, cv.THRESH_BINARY)
        #debug visualization
        #cv.imshow("Segmented Image", img_mask)
        #cv.waitKey(0)
        masked_image = cv.bitwise_and(image, image, mask=all_mask)
        #divide by 255 because of max value
        pixel_count = np.sum(all_mask)/255

        return masked_image, pixel_count

    #averages together all depth readings for detected object
    def calculate_depth(self,depth_image):
        depth = -1
        # get depth image
        depth_image = self.get_depth_image()
        #get segmentation from RGB image and apply max
        masked_image, pixel_count = self.segment_image(depth_image)

        #make into 1d array for easier processing
        flattened_image = masked_image.flatten()
        depth = np.sum(flattened_image, where=flattened_image>0)/pixel_count
        #print(depth)
        #average together readings from depth image
        return depth+0.1


    def get_depth_image(self):
        image_c_ptr = self.depth_camera.getRangeImage(data_type="buffer")
        image_np = np.ctypeslib.as_array(image_c_ptr, (self.depth_camera.getWidth() * self.depth_camera.getHeight(),)).reshape(self.depth_camera.getHeight(), self.depth_camera.getWidth(),1)
        return image_np

    #function for reading out the angle of the position sensor on the robot.
    def calculate_angle(self):
        yaw_angle = self.yaw_axis_motor.getPositionSensor().getValue()
        return yaw_angle

    def update_sensor_readings(self):
        self.current_yaw_axis_angle = self.yaw_axis_motor.getPositionSensor().getValue()
        self.current_pitch_axis_angle = self.pitch_axis_motor.getPositionSensor().getValue()

    def calculate_user_position(self, depth, angle):
        x_pos = depth*math.cos(angle) #pi is added to align gimbal frame to robot frame
        y_pos = depth*math.sin(angle)

        return x_pos, y_pos

    def interpolate_velocity(self, curr_position):
        #calculate current velocity
        curr_x_velocity = (curr_position[0] - self.prev_position[0]) / (self.update_time/1000)
        curr_y_velocity = (curr_position[1] - self.prev_position[1]) / (self.update_time/1000)

        self.prev_position = curr_position

        #push to buffer
        self.x_velocity_buffer[self.velocity_buffer_index] = curr_x_velocity
        self.y_velocity_buffer[self.velocity_buffer_index] = curr_y_velocity

        #implement circular buffer
        self.velocity_buffer_index += 1
        if self.velocity_buffer_index >= len(self.x_velocity_buffer):
            self.velocity_buffer_index = 0

        #average buffer
        x_vel = np.average(self.x_velocity_buffer)
        y_vel = np.average(self.y_velocity_buffer)
        #print(x_vel, y_vel)
        self.prev_velocity = [x_vel, y_vel]

        return x_vel, y_vel

    def estimate_next_position(self, position, velocity):
        next_x_pos = position[0]+velocity[0]*self.update_time
        next_y_pos = position[1]+velocity[1]*self.update_time

        self.next_position = [next_x_pos, next_y_pos]

        return [next_x_pos, next_y_pos]

    #setter function for enabling segmentation (needs to also be set in webot world)
    def enable_segmentation(self, status):
        if status == False:
            #disable segmentation
            self.rgb_camera.disableRecognitionSegmentation()
        else:
            #enable segmentation
            self.rgb_camera.enableRecognitionSegmentation()

    #setter function for enabling recognition
    def enable_recognition(self, status):
        if status == False:
            #disable recognition
            self.rgb_camera.recognitionDisable()
        else:
            #enable recognition
            self.rgb_camera.recognitionEnable(self.update_time)

    # setter function for totally enabling the computer vision pipeline.
    def enable_tracking(self, status):
        self.enable_recognition(status)
        self.enable_segmentation(status)

        self.yaw_axis_motor.getPositionSensor().enable(self.motor_update_time)
        self.pitch_axis_motor.getPositionSensor().enable(self.motor_update_time)

    def calc_pid(self,set_point, current_point, kpid, last_error, error_sum):
        error = set_point - current_point
        p_error = kpid[0]*error
        error_sum += error
        i_error = kpid[1]*error_sum
        d_error = kpid[2]*(error - last_error)
        output = p_error + i_error + d_error
        return output, error, error_sum

    def run(self):
        out_of_range_flag = False
        self.find_user()
        if self.use_estimator:
            self.prev_position = self.estimated_position
        distance = np.sqrt(self.prev_position[0]**2 + self.prev_position[1]**2)
        [vm, va] = self.velocity_mag_angle()
        if distance > self.max_distance:
            out_of_range_flag = True
        return self.prev_position, out_of_range_flag, self.tracking_flag, vm, va

    def calculate_user_position_new(self, depth, angle, user_position_on_image):
        #calculates the distance from left to right given the current depth measurement
        horizontal_distance = np.tan(self.horizontal_fov/2)*depth
        horizontal_displacement = horizontal_distance*(-user_position_on_image[0]/0.5)
        position_in_camera_frame = np.array([depth, horizontal_displacement, 0, 1]).reshape(4,1)

        tf_matrix = np.array([[np.cos(angle), -np.sin(angle), 0, -0.12], [np.sin(angle), np.cos(angle), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

        new_position = np.matmul(tf_matrix, position_in_camera_frame)

        return new_position[0][0], new_position[1][0]

    def velocity_mag_angle(self):
        mag = np.sqrt(np.square(self.prev_velocity[0])+np.square(self.prev_velocity[1]))
        angle = np.arctan2(self.prev_velocity[1],self.prev_velocity[0])
        return mag, angle