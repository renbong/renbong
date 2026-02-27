import unittest

from copper_bar_controller import CopperBarMachine, MachineState, ProcessConfig


class CopperBarMachineTests(unittest.TestCase):
    def test_full_cycle(self):
        machine = CopperBarMachine(ProcessConfig(punch_positions=[120.0, 260.0], cut_position=320.0))

        state, log = machine.run_cycle()

        self.assertEqual(state, MachineState.DONE)
        self.assertIn("检测到铜排", log)
        self.assertIn("夹钳夹紧铜排", log)
        self.assertIn("在 120.0mm 冲孔", log)
        self.assertIn("在 260.0mm 冲孔", log)
        self.assertIn("在 320.0mm 裁切", log)

    def test_invalid_cut_position(self):
        with self.assertRaises(ValueError):
            CopperBarMachine(ProcessConfig(punch_positions=[120.0, 260.0], cut_position=200.0))

    def test_feed_must_move_forward(self):
        machine = CopperBarMachine(ProcessConfig(punch_positions=[100.0], cut_position=200.0))
        machine.detect_copper_bar()
        machine.clamp()
        machine.feed_to(100.0)
        machine.punch_at(100.0)

        with self.assertRaises(RuntimeError):
            machine.feed_to(90.0)


if __name__ == "__main__":
    unittest.main()
