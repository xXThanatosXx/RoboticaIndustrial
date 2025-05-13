#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
from rclpy.action import ActionServer
from arm_msgs.action import armTask
from moveit.planning import MoveItPy
from moveit.core.robot_state import RobotState


class TaskServer(Node):
    def __init__(self):
        super().__init__("task_server")
        self.get_logger().info("Starting the Server")
        self.action_server = ActionServer(
            self, armTask, "task_server", self.goalCallback
        )

        # MoveIt 2 Interface
        self.arm = MoveItPy(node_name="moveit_py")
        self.arm_arm = self.arm.get_planning_component("arm")
        self.arm_gripper = self.arm.get_planning_component("gripper")

    def goalCallback(self, goal_handle):
        self.get_logger().info(
            "Received goal request with id %d" % goal_handle.request.task_number
        )

        arm_state = RobotState(self.arm.get_robot_model())
        gripper_state = RobotState(self.arm.get_robot_model())

        arm_joint_goal = []
        gripper_joint_goal = []

        if goal_handle.request.task_number == 0:
            arm_joint_goal = np.array([0.0, 0.0, 0.0])
            gripper_joint_goal = np.array([-0.7, 0.7])
        elif goal_handle.request.task_number == 1:
            arm_joint_goal = np.array([-1.14, -0.6, -0.07])
            gripper_joint_goal = np.array([0.0, 0.0])
        elif goal_handle.request.task_number == 2:
            arm_joint_goal = np.array([-1.57,0.0,-0.9])
            gripper_joint_goal = np.array([0.0, 0.0])
        else:
            self.get_logger().error("Invalid Task Number")
            return

        arm_state.set_joint_group_positions("arm", arm_joint_goal)
        gripper_state.set_joint_group_positions("gripper", gripper_joint_goal)

        self.arm_arm.set_start_state_to_current_state()
        self.arm_gripper.set_start_state_to_current_state()

        self.arm_arm.set_goal_state(robot_state=arm_state)
        self.arm_gripper.set_goal_state(robot_state=gripper_state)

        arm_plan_result = self.arm_arm.plan()
        gripper_plan_result = self.arm_gripper.plan()

        if arm_plan_result and gripper_plan_result:
            self.get_logger().info("Planner SUCCEED, moving the arm and the gripper")
            self.arm.execute(arm_plan_result.trajectory, controllers=[])
            self.arm.execute(gripper_plan_result.trajectory, controllers=[])
        else:
            self.get_logger().info("One or more planners failed!")
        
        self.get_logger().info("Goal succeeded")
        goal_handle.succeed()
        result = armTask.Result()
        result.success = True
        return result 


def main(args=None):
    rclpy.init(args=args)
    task_server = TaskServer()
    rclpy.spin(task_server)

if __name__ == "__main__":
    main()