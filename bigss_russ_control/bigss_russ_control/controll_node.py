import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory

class JointTrajectoryControllerClient(Node):
    def __init__(self):
        super().__init__('joint_trajectory_controller_client')
        self._client = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller/follow_joint_trajectory')
        self.get_logger().info("Waiting for server to be available...")
        self._client.wait_for_server()

    def send_trajectory(self):
        # Create the trajectory message
        traj = JointTrajectory()
        traj.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]
        
        # Define the four waypoints (ensure these are valid joint limits)
        waypoints = [
            [0.0, -1.57, 0.0, -1.57, 0.0, 0.0],  
            [0.0, -0.6, 1.4, -1.57, 0.0, 0.0],   
            [0.4, -0.6, 1.4, -1.57, 0.0, 0.0],  
            [-0.4, -0.6, 1.4, -1.57, 0.0, 0.0], 
            [0.0, -0.6, 1.4, -1.57, 0.0, 0.0],  
            [0.0, -1.57, 0.0, -1.57, 0.0, 0.0],   
        ]
        
        # Set the time intervals (5 seconds between each point)
        time_from_start = 0
        
        # Loop through the waypoints
        for waypoint in waypoints:
            point = JointTrajectoryPoint()
            point.positions = [float(i) for i in waypoint]  # Ensure positions are floats
            time_from_start += 5  # Add 5 seconds for each waypoint
            point.time_from_start.sec = time_from_start

            traj.points.append(point)

        # Send the trajectory
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = traj
        self.get_logger().info("Sending trajectory...")
        self._client.send_goal_async(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    node = JointTrajectoryControllerClient()
    node.send_trajectory()
    rclpy.spin(node)

if __name__ == '__main__':
    main()

