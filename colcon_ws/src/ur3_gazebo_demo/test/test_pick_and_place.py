import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from action_msgs.msg import GoalStatus
from ur3_gazebo_demo.ur3_pick_and_place import DEFAULTS, PickAndPlace, validate


class PickAndPlaceTests(unittest.TestCase):
    def fake_node(self):
        node = Mock()
        node.config = dict(DEFAULTS, vacuum_settle_time=0.0)
        return node

    def test_sequence(self):
        node = self.fake_node()
        PickAndPlace.run(node)
        events = [(call[0], call[1]) for call in node.mock_calls
                  if call[0] in ("move", "vacuum")]
        self.assertEqual(events, [
            ("vacuum", (False,)), ("move", ("home",)),
            ("move", ("pick_approach",)), ("move", ("pick",)),
            ("vacuum", (True,)), ("move", ("pick_approach",)),
            ("move", ("place_approach",)), ("move", ("place",)),
            ("vacuum", (False,)), ("move", ("place_approach",)),
            ("move", ("home",)),
        ])

    def test_transport_failure_does_not_release(self):
        node = self.fake_node()
        node.move.side_effect = [None, None, None, RuntimeError("aborted")]
        with self.assertRaises(RuntimeError):
            PickAndPlace.run(node)
        self.assertEqual([c.args for c in node.vacuum.call_args_list], [(False,), (True,)])

    def test_d0_and_polarity(self):
        for active_high in (True, False):
            for enabled in (True, False):
                node = self.fake_node()
                node.config["vacuum_active_high"] = active_high
                node.wait.return_value.success = True
                PickAndPlace.vacuum(node, enabled)
                request = node.io.call_async.call_args.args[0]
                self.assertEqual((request.fun, request.pin), (1, 0))
                self.assertEqual(request.state, float(enabled == active_high))

    def test_failed_io_stops_sequence(self):
        node = self.fake_node()
        node.wait.return_value.success = False
        with self.assertRaises(RuntimeError):
            PickAndPlace.vacuum(node, True)

    def test_rejected_and_aborted_moves(self):
        for accepted in (False, True):
            node = self.fake_node()
            node.wait.side_effect = [SimpleNamespace(accepted=accepted,
                get_result_async=Mock()), SimpleNamespace(status=GoalStatus.STATUS_ABORTED,
                result=SimpleNamespace(error_code=-4, error_string="path tolerance"))]
            with self.assertRaises(RuntimeError):
                PickAndPlace.move(node, "pick")

    def test_timeout(self):
        from unittest.mock import patch
        node = self.fake_node()
        future = Mock()
        future.done.return_value = False
        with patch("ur3_gazebo_demo.ur3_pick_and_place.rclpy.spin_until_future_complete"):
            with self.assertRaises(RuntimeError):
                PickAndPlace.wait(node, future, 1.0, "test")

    def test_invalid_configuration(self):
        validate(DEFAULTS)
        for key, value in (("pick", [0.0]), ("place", [float("nan")] * 6),
                           ("motion_timeout", 0.0), ("vacuum_pin", 18)):
            with self.assertRaises(ValueError):
                validate(dict(DEFAULTS, **{key: value}))

    def test_cancel_recovers_pending_goal(self):
        node = self.fake_node()
        node.goal_handle = None
        node.send_future = Mock()
        node.result_future = None
        handle = Mock(accepted=True)
        node.wait.side_effect = [handle, SimpleNamespace(goals_canceling=[1]), Mock()]
        PickAndPlace.cancel_motion(node)
        handle.cancel_goal_async.assert_called_once()
        handle.get_result_async.assert_called_once()

    def test_cancel_rejection_is_reported(self):
        node = self.fake_node()
        node.goal_handle = Mock(accepted=True)
        node.wait.return_value = SimpleNamespace(goals_canceling=[])
        with self.assertRaises(RuntimeError):
            PickAndPlace.cancel_motion(node)


if __name__ == "__main__":
    unittest.main()
