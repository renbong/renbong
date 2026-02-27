# 铜排冲孔/裁切流程控制示例

该示例实现了你描述的自动流程：

1. 检测到铜排
2. 夹钳夹紧铜排
3. 往前送料到对应模具下
4. 在可设定的冲孔位置执行冲孔（可多个）
5. 送料到可设定裁切位置执行裁切

## 使用方法

```python
from copper_bar_controller import CopperBarMachine, ProcessConfig

config = ProcessConfig(
    punch_positions=[120.0, 260.0, 300.0],  # 冲孔位置，可自由设定
    cut_position=360.0,                      # 裁切位置，可自由设定
)
machine = CopperBarMachine(config)
state, log = machine.run_cycle()
print(state)
print("\n".join(log))
```

## 约束

- 冲孔位置必须升序且大于 0。
- 裁切位置必须大于最后一个冲孔位置。
- 送料只能向前。

