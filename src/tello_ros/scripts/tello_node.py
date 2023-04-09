#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from djitellopy import Tello
import threading
import cv2

class CameraPublisher:
    def __init__(self):
        # Initialize the ROS node
        rospy.init_node('camera_publisher', anonymous=True)
        cv2.namedWindow("Controls")

        # Create a publisher for the camera feed
        self.pub = rospy.Publisher('/cam0/image_raw', Image, queue_size=10)

        # Create a DJITelloPy object
        self.drone = Tello()

        # Connect to the drone
        self.drone.connect()

        # Start the video stream
        self.drone.streamon()

        # Create a CvBridge object to convert the image format
        self.bridge = CvBridge()

        # Create a thread to publish the camera feed
        self.camera_thread = threading.Thread(target=self.publish_camera_feed)
        self.camera_thread.daemon = True
        self.camera_thread.start()

        # Loop to listen to keyboard input
        while not rospy.is_shutdown():
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):  # Quit
                self.drone.land()
                break
            elif key == ord('t'):  # Takeoff
                self.drone.takeoff()
            elif key == ord('l'):  # Land
                self.drone.land()
            elif key == ord('w'):  # Move forward
                self.drone.move_forward(30)
            elif key == ord('s'):  # Move backward
                self.drone.move_back(30)
            elif key == ord('a'):  # Move left
                self.drone.move_left(30)
            elif key == ord('d'):  # Move right
                self.drone.move_right(30)
            elif key == ord('u'):  # Move up
                self.drone.move_up(30)
            elif key == ord('j'):  # Move down
                self.drone.move_down(30)

        # Stop the video stream and disconnect from the drone
        self.drone.streamoff()
        self.drone.end()

    def publish_camera_feed(self):
        rate = rospy.Rate(30)
        
        # Loop to publish the camera feed
        while not rospy.is_shutdown():
            # Get the current frame from the drone
            frame = self.drone.get_frame_read().frame

            # Convert the frame to a ROS message
            msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")

            # Publish the message
            self.pub.publish(msg)
            rate.sleep()

if __name__ == '__main__':
    try:
        # Create a CameraPublisher object
        camera_publisher = CameraPublisher()
        # Spin the ROS node
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
