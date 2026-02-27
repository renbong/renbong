from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple


class MachineState(str, Enum):
    IDLE = "idle"
    DETECTED = "detected"
    CLAMPED = "clamped"
    FEEDING = "feeding"
    PUNCHING = "punching"
    CUTTING = "cutting"
    DONE = "done"


@dataclass
class ProcessConfig:
    """Configurable process positions in millimeters."""

    punch_positions: List[float]
    cut_position: float

    def validate(self) -> None:
        if not self.punch_positions:
            raise ValueError("至少需要设置一个冲孔位置")
        if sorted(self.punch_positions) != self.punch_positions:
            raise ValueError("冲孔位置必须按从小到大排序")
        if any(p <= 0 for p in self.punch_positions):
            raise ValueError("冲孔位置必须大于 0")
        if self.cut_position <= self.punch_positions[-1]:
            raise ValueError("裁切位置必须大于最后一个冲孔位置")


@dataclass
class CopperBarMachine:
    config: ProcessConfig
    state: MachineState = MachineState.IDLE
    current_position: float = 0.0
    detected: bool = False
    clamped: bool = False
    process_log: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.config.validate()

    def detect_copper_bar(self) -> None:
        if self.state != MachineState.IDLE:
            raise RuntimeError("当前状态不允许检测")
        self.detected = True
        self.state = MachineState.DETECTED
        self.process_log.append("检测到铜排")

    def clamp(self) -> None:
        if self.state != MachineState.DETECTED:
            raise RuntimeError("未检测到铜排，不能夹紧")
        self.clamped = True
        self.state = MachineState.CLAMPED
        self.process_log.append("夹钳夹紧铜排")

    def feed_to(self, position: float) -> None:
        if self.state not in {MachineState.CLAMPED, MachineState.FEEDING, MachineState.PUNCHING}:
            raise RuntimeError("当前状态不允许送料")
        if position <= self.current_position:
            raise RuntimeError("送料目标位置必须大于当前位置")
        self.state = MachineState.FEEDING
        self.current_position = position
        self.process_log.append(f"送料到 {position:.1f}mm")

    def punch_at(self, position: float) -> None:
        if self.state != MachineState.FEEDING:
            raise RuntimeError("需先送料到位后冲孔")
        if abs(self.current_position - position) > 1e-6:
            raise RuntimeError("当前不在设定冲孔位置")
        self.state = MachineState.PUNCHING
        self.process_log.append(f"在 {position:.1f}mm 冲孔")

    def cut(self) -> None:
        if self.state != MachineState.FEEDING:
            raise RuntimeError("需先送料到裁切位置")
        if abs(self.current_position - self.config.cut_position) > 1e-6:
            raise RuntimeError("当前不在设定裁切位置")
        self.state = MachineState.CUTTING
        self.process_log.append(f"在 {self.current_position:.1f}mm 裁切")
        self.state = MachineState.DONE
        self.process_log.append("工序完成")

    def run_cycle(self) -> Tuple[MachineState, List[str]]:
        """Execute one full process cycle.

        Flow:
        1) detect copper bar
        2) clamp
        3) feed and punch for each configured punch position
        4) feed to cut position and cut
        """
        self.detect_copper_bar()
        self.clamp()
        for p in self.config.punch_positions:
            self.feed_to(p)
            self.punch_at(p)
        self.feed_to(self.config.cut_position)
        self.cut()
        return self.state, self.process_log
