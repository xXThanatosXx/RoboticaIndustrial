"""Single joint-space pick/place cycle with a digital vacuum valve."""

import math
import time

import rclpy
from action_msgs.msg import GoalStatus
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from trajectory_msgs.msg import JointTrajectoryPoint
from ur_msgs.srv import SetIO

from .ur3_joint_trajectory import JOINT_NAMES


DEFAULTS = {
    "controller_name": "scaled_joint_trajectory_controller",
    "io_service": "/io_and_status_controller/set_io",
    "vacuum_pin": 0,
    "vacuum_active_high": True,
    "joint_prefix": "",
    "move_duration": 4.0,
    "server_timeout": 10.0,
    "motion_timeout": 120.0,
    "io_timeout": 5.0,
    "vacuum_settle_time": 1.0,
    "home": [0.0, -1.57, 1.57, -1.57, -1.57, 0.0],
    "pick_approach": [0.35, -1.40, 1.35, -1.52, -1.57, 0.0],
    "pick": [0.35, -1.20, 1.35, -1.72, -1.57, 0.0],
    "place_approach": [-0.35, -1.40, 1.35, -1.52, -1.57, 0.0],
    "place": [-0.35, -1.20, 1.35, -1.72, -1.57, 0.0],
}


def validate(config):
    for name in ("home", "pick_approach", "pick", "place_approach", "place"):
        if len(config[name]) != 6 or not all(math.isfinite(v) for v in config[name]):
            raise ValueError(f"{name}: se requieren seis ángulos finitos en radianes")
    for name in ("move_duration", "server_timeout", "motion_timeout", "io_timeout"):
        if not math.isfinite(config[name]) or config[name] <= 0:
            raise ValueError(f"{name} debe ser positivo y finito")
    if not math.isfinite(config["vacuum_settle_time"]) or config["vacuum_settle_time"] < 0:
        raise ValueError("vacuum_settle_time debe ser finito y no negativo")
    if not 0 <= config["vacuum_pin"] <= 17:
        raise ValueError("vacuum_pin debe estar entre 0 y 17; D0 es 0")


class PickAndPlace(Node):
    def __init__(self):
        super().__init__("ur3_pick_and_place")
        self.config = {
            name: self.declare_parameter(name, default).value
            for name, default in DEFAULTS.items()
        }
        validate(self.config)
        controller = self.config["controller_name"].strip("/")
        self.client = ActionClient(self, FollowJointTrajectory,
                                   f"/{controller}/follow_joint_trajectory")
        self.io = self.create_client(SetIO, self.config["io_service"])
        self.goal_handle = None
        self.result_future = None
        self.send_future = None

    def wait(self, future, seconds, description):
        rclpy.spin_until_future_complete(self, future, timeout_sec=seconds)
        if not future.done():
            raise RuntimeError(f"Tiempo agotado: {description}")
        return future.result()

    def move(self, name):
        self.get_logger().info(f"Movimiento: {name}")
        self.result_future = None
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = [self.config["joint_prefix"] + j for j in JOINT_NAMES]
        nanoseconds = round(self.config["move_duration"] * 1e9)
        point = JointTrajectoryPoint()
        point.positions = list(self.config[name])
        point.velocities = [0.0] * 6
        point.time_from_start = Duration(sec=nanoseconds // 10**9,
                                        nanosec=nanoseconds % 10**9)
        goal.trajectory.points = [point]
        goal.goal_time_tolerance = Duration(sec=2)
        self.send_future = self.client.send_goal_async(goal)
        self.goal_handle = self.wait(self.send_future, self.config["server_timeout"],
                                     "aceptación de trayectoria")
        self.send_future = None
        if not self.goal_handle.accepted:
            self.goal_handle = None
            raise RuntimeError(f"Trayectoria rechazada: {name}")
        self.result_future = self.goal_handle.get_result_async()
        result = self.wait(self.result_future, self.config["motion_timeout"], name)
        self.goal_handle = None
        if (result.status != GoalStatus.STATUS_SUCCEEDED or
                result.result.error_code != FollowJointTrajectory.Result.SUCCESSFUL):
            raise RuntimeError(f"Falló {name}: estado={result.status}, "
                               f"código={result.result.error_code}, {result.result.error_string}")

    def vacuum(self, enabled):
        request = SetIO.Request()
        request.fun = SetIO.Request.FUN_SET_DIGITAL_OUT
        request.pin = self.config["vacuum_pin"]
        request.state = float(enabled == self.config["vacuum_active_high"])
        response = self.wait(self.io.call_async(request), self.config["io_timeout"], "SetIO")
        if not response.success:
            raise RuntimeError("El driver rechazó el cambio de la ventosa")
        self.get_logger().info(f"Ventosa {'ON' if enabled else 'OFF'} (pin {request.pin})")
        # Wall time: do not depend on /clock being published by URSim.
        deadline = time.monotonic() + self.config["vacuum_settle_time"]
        while time.monotonic() < deadline:
            if not rclpy.ok():
                raise RuntimeError("ROS detenido durante la espera de la ventosa")
            rclpy.spin_once(self, timeout_sec=min(0.1, max(0.0, deadline - time.monotonic())))

    def run(self):
        if not self.client.wait_for_server(timeout_sec=self.config["server_timeout"]):
            raise RuntimeError("No está disponible el controlador de trayectoria")
        if not self.io.wait_for_service(timeout_sec=self.config["server_timeout"]):
            raise RuntimeError("No está disponible el servicio SetIO")
        self.vacuum(False)
        self.move("home")
        self.move("pick_approach")
        self.move("pick")
        self.vacuum(True)
        self.move("pick_approach")
        self.move("place_approach")
        self.move("place")
        self.vacuum(False)
        self.move("place_approach")
        self.move("home")
        self.get_logger().info("Pick and place completado")

    def cancel_motion(self):
        # A timed-out goal submission may still have been accepted by the server.
        if self.goal_handle is None and self.send_future is not None:
            self.goal_handle = self.wait(self.send_future, self.config["server_timeout"],
                                         "recuperación de objetivo pendiente")
        if self.goal_handle is not None and self.goal_handle.accepted:
            response = self.wait(self.goal_handle.cancel_goal_async(), 5.0, "cancelación")
            if not response.goals_canceling:
                raise RuntimeError("El controlador no confirmó la cancelación; comprobar su estado")
            result_future = (self.result_future if self.result_future is not None
                             else self.goal_handle.get_result_async())
            self.wait(result_future, 5.0, "fin del movimiento cancelado")


def main(args=None):
    # Keep the ROS context alive on Ctrl+C long enough to request cancellation.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = None
    exit_code = 0
    try:
        node = PickAndPlace()
        node.run()
    except (Exception, KeyboardInterrupt) as error:
        exit_code = 1
        if node is not None:
            node.get_logger().error(f"Secuencia interrumpida: {error}. No se ordenará soltar la pieza.")
            try:
                node.cancel_motion()
            except Exception as cancel_error:
                node.get_logger().error(f"No se pudo confirmar la parada: {cancel_error}")
        else:
            print(f"No se pudo iniciar el ejemplo: {error}")
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
