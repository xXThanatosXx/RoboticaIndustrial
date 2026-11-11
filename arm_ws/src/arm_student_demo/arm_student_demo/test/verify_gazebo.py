"""Prueba de tres ciclos en Gazebo sin interfaz grafica ni hardware.
Ejecutar tras compilar y cargar install/setup.bash.
"""
import argparse
import os
import yaml
from pathlib import Path
import signal
import subprocess
import time

# Dominio y puerto separados de las sesiones habituales del laboratorio.
os.environ['ROS_DOMAIN_ID'] = '174'
os.environ['ROS_LOCALHOST_ONLY'] = '1'
os.environ['GAZEBO_MASTER_URI'] = 'http://127.0.0.1:11359'
os.environ['GAZEBO_MODEL_DATABASE_URI'] = ''
os.environ['ROS_LOG_DIR'] = '/tmp/arm_student_demo_logs'

import rclpy
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from sensor_msgs.msg import JointState


def stop(process):
    if process is not None and process.poll() is None:
        os.killpg(process.pid, signal.SIGINT)
        try:
            process.wait(timeout=12)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', action='store_true')
    variant = parser.parse_args().variant
    cycles = 1 if variant else 3
    robot = None
    sequence = None
    node = None
    states = []
    rclpy.init()
    try:
        with open('/tmp/arm_student_gazebo.log', 'w') as log:
            robot = subprocess.Popen([
                'ros2', 'launch', 'arm_student_demo', 'robot.launch.py', 'gui:=false',
            ], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        node = Node('student_verification')
        node.create_subscription(JointState, '/joint_states', states.append, 100)
        clients = [ActionClient(node, FollowJointTrajectory, '/' + name + '/follow_joint_trajectory')
                   for name in ['arm_controller', 'gripper_controller']]
        deadline = time.monotonic() + 75
        while not all(client.server_is_ready() for client in clients):
            rclpy.spin_once(node, timeout_sec=0.1)
            if time.monotonic() > deadline:
                raise RuntimeError('Gazebo no inicio: ver /tmp/arm_student_gazebo.log')
        print('Controladores disponibles en Gazebo', flush=True)
        config = Path(__file__).parents[1] / 'config' / 'sequence.yaml'
        command = ['ros2', 'run', 'arm_student_demo', 'sequence_controller', '--ros-args',
                   '--params-file', str(config), '-p', 'use_sim_time:=true', '-p', 'repetitions:=3']
        if variant:
            data = yaml.safe_load(config.read_text())
            data['sequence_controller']['ros__parameters'].update({
                'position_a': [-0.35, -0.10, 0.15], 'position_b': [0.15, -0.20, 0.05],
                'move_seconds': 6.0, 'pause_seconds': 2.0, 'repetitions': 1,
            })
            config = Path('/tmp/arm_student_variant.yaml')
            config.write_text(yaml.safe_dump(data))
            command = ['ros2', 'launch', 'arm_student_demo', 'sequence.launch.py',
                       'is_sim:=true', 'config:=' + str(config)]
        with open('/tmp/arm_student_sequence.log', 'w') as log:
            sequence = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                        start_new_session=True)
        deadline = time.monotonic() + 180
        while sequence.poll() is None:
            rclpy.spin_once(node, timeout_sec=0.1)
            if time.monotonic() > deadline:
                raise RuntimeError('La rutina excedio el tiempo de prueba')
        assert sequence.returncode == 0, Path('/tmp/arm_student_sequence.log').read_text()
        report = Path('/tmp/arm_student_sequence.log').read_text()
        assert report.count('Movimiento completado') == 7 * cycles
        assert 'SECUENCIA COMPLETADA' in report
        assert len(states) > 20
        for joint in ['joint_1', 'joint_2', 'joint_3', 'joint_4']:
            values = [dict(zip(s.name, s.position))[joint] for s in states if joint in s.name]
            assert values, f'Sin datos de {joint}'
            print(f'{joint}: min={min(values):.4f}, max={max(values):.4f}, final={values[-1]:.4f}')
            assert max(values) - min(values) > 0.04, f'{joint} no cambio'
            target = -0.35 if joint == 'joint_4' else 0.0
            assert abs(values[-1] - target) < 0.05, f'{joint}: no regreso a destino'
        print(f'PASS: {cycles} ciclos, {7 * cycles} movimientos, {len(states)} mensajes JointState')
    finally:
        stop(sequence)
        stop(robot)
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
