import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class ReadJoints(Node):
    def __init__(self):
        super().__init__('read_joints')
        self.subscription = self.create_subscription(
            JointState, '/estado_brazo', self.show_positions, 10)

    def show_positions(self, message):
        values = []
        for name, angle in zip(message.name, message.position):
            if name in ['joint_1', 'joint_2', 'joint_3']:
                values.append(
                    f'{name}: {angle:.2f} rad = {math.degrees(angle):.1f} grados')
        self.get_logger().info(' | '.join(values), throttle_duration_sec=1.0)


def main(args=None):
    rclpy.init(args=args)
    node = ReadJoints()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()



if __name__ == '__main__':
    main()
