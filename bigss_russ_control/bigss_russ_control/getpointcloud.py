import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
import numpy as np
import open3d as o3d
import cv2
from cv_bridge import CvBridge
import matplotlib.pyplot as plt


class PointCloudGenerator(Node):
    def __init__(self):
        super().__init__('pointcloud_generator')
        
        self.bridge = CvBridge()
        self.color_image = None
        self.depth_image = None
        self.intrinsics = None  # Will be set when camera_info is received

        # Subscribe to ROS topics
        self.color_sub = self.create_subscription(Image, "/rgbd_camera/image", self.color_callback, 10)
        self.depth_sub = self.create_subscription(Image, "/rgbd_camera/depth_image", self.depth_callback, 10)
        self.camera_info_sub = self.create_subscription(CameraInfo, "/rgbd_camera/camera_info", self.camera_info_callback, 10)

        # Timer to process point cloud at 10Hz
        self.timer = self.create_timer(0.1, self.process_point_cloud)

        # self.vis = o3d.visualization.Visualizer()
        # self.vis.create_window(window_name="PointCloud Video", width=640, height=480)


    def camera_info_callback(self, msg):
        """Extracts camera intrinsics from CameraInfo message."""
        if self.intrinsics is None: 
            k = msg.k  # 3x3 intrinsic matrix
            self.intrinsics = o3d.camera.PinholeCameraIntrinsic(
                width=msg.width, height=msg.height,
                fx=k[0], fy=k[4], cx=k[2], cy=k[5]
            )
            self.get_logger().info("Updated Camera Intrinsics from /rgbd_camera/camera_info")

    def color_callback(self, msg):
        """Stores latest color image."""
        self.color_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")

    def depth_callback(self, msg):
        # self.get_logger().info("Updated Depth Camera from /rgbd_camera/depth_camera")
        """Stores latest depth image."""
        self.depth_image = self.bridge.imgmsg_to_cv2(msg, "32FC1")
        # self.visualize_images()


    def visualize_images(self):
    # Display the color image
        if self.color_image is not None:
            plt.subplot(1, 2, 1)
            plt.imshow(self.color_image)
            plt.title("Color Image")
            plt.axis("off")  # Turn off axis for clarity

        # Display the depth image
        if self.depth_image is not None:
            # Normalize depth image for display purposes
            depth_display = np.array(self.depth_image, dtype=np.float32)
            depth_display = np.clip(depth_display, 0, 1000)  # Clip depth values to a range (e.g., 0-1000)
            plt.subplot(1, 2, 2)
            plt.imshow(depth_display, cmap='plasma')  # Use 'plasma' or 'gray' colormap for depth images
            plt.title("Depth Image")
            plt.axis("off")

        plt.show()

    def process_point_cloud(self):

        self.visualize_images()
        
        """Processes and visualizes point cloud at 10Hz if data is available."""
        if self.color_image is None or self.depth_image is None or self.intrinsics is None:
            return  # Wait until all data is received

        # Convert OpenCV images to Open3D format

        color_raw = o3d.geometry.Image(self.color_image)
        # # Convert Open3D Image to NumPy array for visualization
        # color_np = np.asarray(color_raw)

        # # Visualize using Matplotlib
        # plt.imshow(color_np)
        # plt.axis('off')  # Hide axis
        # plt.show()

        #depth_raw = o3d.geometry.Image(self.depth_image.astype(np.uint16))
        depth_raw = o3d.geometry.Image(self.depth_image)

                # # Convert Open3D Image to NumPy array for visualization
        # depth_np = np.asarray(depth_raw)

        # # Visualize using Matplotlib
        # plt.imshow(depth_np)
        # plt.axis('off')  # Hide axis
        # plt.show()

        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color_raw, depth_raw, convert_rgb_to_intensity=False
        )

        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, self.intrinsics)
        pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

        o3d.visualization.draw_geometries([pcd])
        self.get_logger().info("Generated and displayed Point Cloud at 10Hz")
        # Update the point cloud in the visualizer
        # self.vis.clear_geometries()  # Clear previous geometries
        # self.vis.add_geometry(pcd)  # Add the new point cloud

        # # Access the ViewControl object to manipulate the camera
        # view_control = self.vis.get_view_control()

        # # Set the camera view parameters to select an angle
        # view_control.set_front([0.5, -1.5, 1.0])  # Camera facing in the direction of (0.5, -1, 0.5)
        # view_control.set_lookat([0, 0, 0])       # Camera looks at the origin (0, 0, 0)
        # view_control.set_up([0, 0, 1])           # Camera up is along the Z-axis
        # view_control.set_zoom(0.8)               # Zoom factor


        # # Update the visualization
        # self.vis.poll_events()
        # self.vis.update_renderer()

        # self.get_logger().info("Updated Point Cloud in Video Feed")


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudGenerator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()