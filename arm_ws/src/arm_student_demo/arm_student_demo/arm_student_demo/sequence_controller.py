"""Una secuencia corta: inicio, A, cerrar, B, abrir, inicio."""
import math
import time

import rclpy
from action_msgs.msg import GoalStatus
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from trajectory_msgs.msg import JointTrajectoryPoint


class SequenceController(Node):
    def __init__(self):
        super().__init__('sequence_controller')
        defaults = {
            'home': [0.0, 0.0, 0.0],
            'position_a': [-0.25, -0.15, 0.10],
            'position_b': [0.25, -0.15, 0.10],
            'gripper_open': -0.35, 'gripper_closed': -0.05,
            'move_seconds': 4.0, 'pause_seconds': 1.0,
            'repetitions': 1, 'server_timeout': 15.0, 'result_margin': 10.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        self.active_goal = None
        self.pending_goal = None
        self.arm = ActionClient(self, FollowJointTrajectory,
                                '/arm_controller/follow_joint_trajectory')
        self.gripper = ActionClient(self, FollowJointTrajectory,
                                    '/gripper_controller/follow_joint_trajectory')

    def value(self, name):
        return self.get_parameter(name).value

    def validate(self):
        for name in ['home', 'position_a', 'position_b']:
            values = self.value(name)
            if len(values) != 3:
                raise ValueError(f'{name}: se necesitan tres posiciones')
            for angle in values:
                if not math.isfinite(angle) or abs(angle) > math.pi / 2:
                    raise ValueError(f'{name}: fuera de los limites del URDF')
        for name in ['gripper_open', 'gripper_closed']:
            angle = self.value(name)
            if not math.isfinite(angle) or not -math.pi / 2 <= angle <= 0:
                raise ValueError(f'{name}: debe estar entre -pi/2 y 0')
        for name in ['move_seconds', 'server_timeout', 'result_margin']:
            if not math.isfinite(self.value(name)) or self.value(name) <= 0:
                raise ValueError(f'{name}: debe ser positivo y finito')
        pause = self.value('pause_seconds')
        if not math.isfinite(pause) or pause < 0:
            raise ValueError('pause_seconds: debe ser finito y no negativo')
        if self.value('repetitions') < 1:
            raise ValueError('repetitions: debe ser al menos 1')

    def wait(self, future, seconds):
        rclpy.spin_until_future_complete(self, future, timeout_sec=seconds)
        if not future.done():
            raise RuntimeError('Tiempo de espera agotado')
        return future.result()

    def move(self, client, joints, positions, label):
        self.get_logger().info(label)
        point = JointTrajectoryPoint()
        point.positions = list(positions)
        nanoseconds = round(self.value('move_seconds') * 1_000_000_000)
        point.time_from_start.sec = nanoseconds // 1_000_000_000
        point.time_from_start.nanosec = nanoseconds % 1_000_000_000
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = joints
        goal.trajectory.points = [point]
        self.pending_goal = client.send_goal_async(goal)
        self.active_goal = self.wait(self.pending_goal, self.value('server_timeout'))
        self.pending_goal = None
        if not self.active_goal.accepted:
            self.active_goal = None
            raise RuntimeError('El controlador rechazo el objetivo')
        response = self.wait(self.active_goal.get_result_async(),
                             self.value('move_seconds') + self.value('result_margin'))
        self.active_goal = None
        if (response.status != GoalStatus.STATUS_SUCCEEDED
                or response.result.error_code != FollowJointTrajectory.Result.SUCCESSFUL):
            raise RuntimeError(f'Movimiento fallido: {response.result.error_string}')
        self.get_logger().info('Movimiento completado')
        time.sleep(self.value('pause_seconds'))

    def run_sequence(self):
        self.validate()
        for client in [self.arm, self.gripper]:
            if not client.wait_for_server(timeout_sec=self.value('server_timeout')):
                raise RuntimeError('Controlador no disponible; inicia robot.launch.py')
        arm_joints = ['joint_1', 'joint_2', 'joint_3']
        steps = [
            (self.arm, arm_joints, self.value('home'), 'Inicio'),
            (self.gripper, ['joint_4'], [self.value('gripper_open')], 'Abrir pinza'),
            (self.arm, arm_joints, self.value('position_a'), 'Posicion A'),
            (self.gripper, ['joint_4'], [self.value('gripper_closed')], 'Cerrar pinza'),
            (self.arm, arm_joints, self.value('position_b'), 'Posicion B'),
            (self.gripper, ['joint_4'], [self.value('gripper_open')], 'Soltar'),
            (self.arm, arm_joints, self.value('home'), 'Regresar'),
        ]
        for cycle in range(self.value('repetitions')):
            self.get_logger().info(f'Ciclo {cycle + 1}/{self.value("repetitions")}')
            for client, joints, positions, label in steps:
                self.move(client, joints, positions, label)
        self.get_logger().info('SECUENCIA COMPLETADA')

    def cancel_motion(self):
        # Recuperar una aceptacion tardia antes de intentar cancelar.
        if self.pending_goal is not None:
            try:
                self.active_goal = self.wait(self.pending_goal, 2.0)
            except RuntimeError:
                self.get_logger().error('Sin respuesta: no se pudo confirmar la cancelacion')
        if self.active_goal is not None and self.active_goal.accepted:
            try:
                response = self.wait(self.active_goal.cancel_goal_async(), 2.0)
                if not response.goals_canceling:
                    self.get_logger().warning('El controlador no confirmo la cancelacion')
                else:
                    self.get_logger().info('Cancelacion aceptada por el controlador')
            except RuntimeError:
                self.get_logger().error('No se pudo confirmar la cancelacion')


def main(args=None):
    # Mantener ROS activo durante Ctrl+C para poder solicitar la cancelacion.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = None
    exit_code = 0
    try:
        node = SequenceController()
        node.run_sequence()
    except KeyboardInterrupt:
        exit_code = 130
    except Exception as error:
        if node is not None:
            node.get_logger().error(str(error))
        else:
            print(error)
        exit_code = 1
    finally:
        if node is not None:
            node.cancel_motion()
            node.destroy_node()
        rclpy.shutdown()
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
