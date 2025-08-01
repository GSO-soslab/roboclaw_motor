from launch import LaunchDescription
import os
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    robot_name = 'test'

    param_file = os.path.join(get_package_share_directory('roboclaw_motor'), 
                              'config', 'param.yaml') 

    return LaunchDescription([
        Node(
            package='roboclaw_motor',
            executable='roboclaw_motor_driver_node',
            name='roboclaw_motor_driver',
            namespace=robot_name,
            output='screen',
            parameters=[param_file]
        ),
    ])
