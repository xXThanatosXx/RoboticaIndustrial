"""Pruebas: validacion y contratos de acciones ROS, sin hardware."""
import math
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
import rclpy
import yaml
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter

from arm_student_demo.sequence_controller import SequenceController
import arm_student_demo.sequence_controller as sequence_module


@pytest.fixture
def values():
    path = Path(__file__).parents[1] / 'config' / 'sequence.yaml'
    return yaml.safe_load(path.read_text())['sequence_controller']['ros__parameters']


@pytest.mark.parametrize('name,value', [
    ('position_a', [0.0, 0.0]), ('position_b', [2.0, 0.0, 0.0]),
    ('home', [math.nan, 0.0, 0.0]), ('gripper_open', 0.1),
    ('gripper_closed', -2.0), ('move_seconds', 0.0),
    ('pause_seconds', -1.0), ('result_margin', math.inf), ('repetitions', 0),
])
def test_invalid_parameters(values, name, value):
    values[name] = value
    with pytest.raises(ValueError):
        SequenceController.validate(SimpleNamespace(value=values.__getitem__))


def test_default_parameters(values):
    SequenceController.validate(SimpleNamespace(value=values.__getitem__))


@pytest.fixture
def ros(monkeypatch):
    prefix = '/student_test/test_' + uuid4().hex
    # Sustituir solo las rutas de los clientes; nunca usar acciones del robot.
    def test_client(node, action_type, name):
        target = prefix + ('/arm' if name.startswith('/arm_controller/') else '/gripper')
        return ActionClient(node, action_type, target)
    monkeypatch.setattr(sequence_module, 'ActionClient', test_client)
    rclpy.init()
    yield prefix
    rclpy.shutdown()


class TestControllers(Node):
    __test__ = False

    def __init__(self, mode, prefix):
        super().__init__('test_controllers')
        self.mode = mode
        self.received = []
        self.canceled = False
        self.servers = [ActionServer(
            self, FollowJointTrajectory, name,
            execute_callback=self.execute,
            goal_callback=self.accept,
            cancel_callback=lambda goal: CancelResponse.ACCEPT,
        ) for name in [prefix + '/arm', prefix + '/gripper']]

    def accept(self, request):
        if self.mode == 'reject':
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def execute(self, handle):
        self.received.append(handle.request.trajectory)
        result = FollowJointTrajectory.Result()
        if self.mode == 'abort':
            handle.abort()
            result.error_code = result.PATH_TOLERANCE_VIOLATED
        elif self.mode == 'timeout':
            deadline = time.monotonic() + 3.0
            while not handle.is_cancel_requested and time.monotonic() < deadline:
                time.sleep(0.01)
            if handle.is_cancel_requested:
                self.canceled = True
                handle.canceled()
            else:
                handle.abort()
        else:
            handle.succeed()
            result.error_code = result.SUCCESSFUL
        return result


@pytest.mark.parametrize('mode', ['success', 'reject', 'abort', 'timeout'])
def test_action_sequence(ros, mode):
    server = TestControllers(mode, ros)
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(server)
    worker = threading.Thread(target=executor.spin)
    worker.start()
    node = SequenceController()
    node.set_parameters([
        Parameter('move_seconds', value=0.05),
        Parameter('pause_seconds', value=0.0),
        Parameter('result_margin', value=0.2),
        Parameter('repetitions', value=3),
    ])
    try:
        if mode == 'success':
            node.run_sequence()
            assert len(server.received) == 21
            first_cycle = server.received[:7]
            assert [t.joint_names for t in first_cycle] == [
                ['joint_1', 'joint_2', 'joint_3'], ['joint_4'],
                ['joint_1', 'joint_2', 'joint_3'], ['joint_4'],
                ['joint_1', 'joint_2', 'joint_3'], ['joint_4'],
                ['joint_1', 'joint_2', 'joint_3']]
            assert list(first_cycle[2].points[0].positions) == node.value('position_a')
            assert list(first_cycle[4].points[0].positions) == node.value('position_b')
            assert first_cycle[0].points[0].time_from_start.nanosec == 50_000_000
        else:
            message = {'reject': 'rechazo', 'abort': 'Movimiento fallido',
                       'timeout': 'Tiempo de espera agotado'}[mode]
            with pytest.raises(RuntimeError, match=message):
                node.run_sequence()
            node.cancel_motion()
            if mode == 'timeout':
                deadline = time.monotonic() + 2.0
                while not server.canceled and time.monotonic() < deadline:
                    time.sleep(0.01)
                assert server.canceled
            assert len(server.received) <= 1
    finally:
        node.destroy_node()
        executor.shutdown()
        worker.join(timeout=5.0)
        for action in server.servers:
            action.destroy()
        server.destroy_node()


def test_missing_server(ros):
    node = SequenceController()
    node.set_parameters([Parameter('server_timeout', value=0.1)])
    try:
        with pytest.raises(RuntimeError, match='Controlador no disponible'):
            node.run_sequence()
    finally:
        node.destroy_node()
