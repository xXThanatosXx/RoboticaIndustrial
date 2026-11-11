import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description = get_package_share_directory('arm_description')
    controller = get_package_share_directory('arm_controller')
    gazebo = get_package_share_directory('gazebo_ros')
    is_sim = LaunchConfiguration('is_sim')
    model = ParameterValue(Command([
        'xacro ', os.path.join(description, 'urdf', 'arm.urdf.xacro'),
        ' is_sim:=true',
    ]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument('is_sim', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(gazebo, 'launch', 'gazebo.launch.py')),
            condition=IfCondition(is_sim),
            launch_arguments={'gui': LaunchConfiguration('gui')}.items(),
        ),
        Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            condition=IfCondition(is_sim),
            parameters=[{'robot_description': model, 'use_sim_time': True}],
        ),
        Node(
            package='gazebo_ros', executable='spawn_entity.py',
            condition=IfCondition(is_sim), output='screen',
            arguments=['-entity', 'arm', '-topic', 'robot_description'],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                controller, 'launch', 'controller.launch.py')),
            launch_arguments={'is_sim': is_sim}.items(),
        ),
    ])