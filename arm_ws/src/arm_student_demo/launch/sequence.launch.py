import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('arm_student_demo')
    return LaunchDescription([
        DeclareLaunchArgument('is_sim', default_value='true'),
        DeclareLaunchArgument('config', default_value=os.path.join(
            share, 'config', 'sequence.yaml')),
        Node(
            package='arm_student_demo', executable='sequence_controller',
            output='screen',
            parameters=[LaunchConfiguration('config'), {
                'use_sim_time': ParameterValue(LaunchConfiguration('is_sim'), value_type=bool),
            }],
        ),
    ])