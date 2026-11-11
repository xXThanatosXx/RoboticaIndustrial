"""Enviar cuatro posiciones al brazo simulado."""
import time

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


def create_trajectory():
    trajectory = JointTrajectory()
    trajectory.joint_names = ['joint_1', 'joint_2', 'joint_3']
    positions = [
        [0.0, 0.0, 0.0],       # Inicio
        [-0.25, -0.15, 0.10],  # Posicion A
        [0.25, -0.15, 0.10],   # Posicion B
        [0.0, 0.0, 0.0],       # Regreso
    ]
    for index, angles in enumerate(positions):
        point = JointTrajectoryPoint()
        point.positions = angles
        point.time_from_start.sec = (index + 1) * 4
        trajectory.points.append(point)
    return trajectory


def main(args=None):
    rclpy.init(args=args)
    node = Node('send_trajectory')
    publisher = node.create_publisher(
        JointTrajectory, '/arm_controller/joint_trajectory', 10)
    try:
        deadline = time.monotonic() + 10.0
        while publisher.get_subscription_count() == 0:
            if time.monotonic() > deadline:
                node.get_logger().error('No hay suscriptores. Revisa los controladores.')
                return 1
            rclpy.spin_once(node, timeout_sec=0.1)
        publisher.publish(create_trajectory())
        if not publisher.wait_for_all_acked(Duration(seconds=2)):
            node.get_logger().error('No se confirmo la entrega del mensaje.')
            return 1
        node.get_logger().info('Trayectoria enviada. Observa los 16 segundos en Gazebo.')
        return 0
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
