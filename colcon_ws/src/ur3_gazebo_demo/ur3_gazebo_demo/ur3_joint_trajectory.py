#!/usr/bin/env python3

from typing import List

import rclpy
from action_msgs.msg import GoalStatus
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from control_msgs.msg import JointTolerance
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint


JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]


class UR3GazeboTrajectoryClient(Node):
    def __init__(self) -> None:
        super().__init__("ur3_gazebo_trajectory_client")
        self.declare_parameter("controller_name", "joint_trajectory_controller")
        controller_name = self.get_parameter("controller_name").get_parameter_value().string_value
        action_name = f"/{controller_name}/follow_joint_trajectory"

        self._client = ActionClient(self, FollowJointTrajectory, action_name)
        self.get_logger().info(f"Esperando servidor de accion en {action_name}")
        self._client.wait_for_server()

        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINT_NAMES
        goal.trajectory.points = self._build_points()
        goal.goal_time_tolerance = Duration(sec=1)
        goal.goal_tolerance = [
            JointTolerance(name=joint_name, position=0.02, velocity=0.05)
            for joint_name in JOINT_NAMES
        ]

        self.get_logger().info("Enviando trayectoria de demostracion al UR3 en Gazebo")
        send_future = self._client.send_goal_async(goal)
        send_future.add_done_callback(self._goal_response_callback)

    def _build_points(self) -> List[JointTrajectoryPoint]:
        waypoints = [
            ([0.0, -1.57, 1.57, -1.57, -1.57, 0.0], 2.0),
            ([0.35, -1.20, 1.35, -1.75, -1.57, 0.25], 5.0),
            ([-0.35, -1.20, 1.35, -1.75, -1.57, -0.25], 8.0),
            ([0.0, -1.57, 1.57, -1.57, -1.57, 0.0], 11.0),
        ]

        points: List[JointTrajectoryPoint] = []
        for positions, seconds in waypoints:
            point = JointTrajectoryPoint()
            point.positions = positions
            point.velocities = [0.0] * len(JOINT_NAMES)
            point.time_from_start = Duration(sec=int(seconds), nanosec=int((seconds % 1) * 1e9))
            points.append(point)
        return points

    def _goal_response_callback(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("La trayectoria fue rechazada por el controlador")
            rclpy.shutdown()
            return

        self.get_logger().info("Trayectoria aceptada, esperando resultado")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _result_callback(self, future) -> None:
        result = future.result()
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Trayectoria completada correctamente")
        else:
            self.get_logger().error(
                f"La trayectoria fallo con estado {result.status} y mensaje: "
                f"{result.result.error_string}"
            )
        rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = UR3GazeboTrajectoryClient()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
