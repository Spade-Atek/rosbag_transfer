# Rosbag Transfer

在 ROS1 bag 与 ROS2 db3 格式之间互转。（Livox Mid360 激光雷达采集的数据包）

## 项目结构

```
rosbag_transfer/
├── msg/
│   ├── CustomMsg.msg
│   └── CustomPoint.msg
├── scripts/
│   ├── db3_to_bag.py    # ROS2 db3  -> ROS1 bag
│   └── bag_to_db3.py    # ROS1 bag  -> ROS2 db3
├── CMakeLists.txt
├── package.xml
└── README.md
```

## 功能特点

- 双向转换：ROS2 db3 ↔ ROS1 bag
- 支持 Livox Mid360 激光雷达自定义消息类型 (`livox_ros_driver2/msg/CustomMsg`)
- 支持标准 IMU 消息 (`sensor_msgs/msg/Imu`)
- 自动保留原始时间戳和话题信息

## 依赖

转换脚本只依赖 Python 和 `rosbags` 库，**不依赖任何 ROS 运行时**，因此在 ROS1 / ROS2 / 纯 Python 环境下均可直接运行。

- Python 3.8+
- rosbags 库

```bash
pip install rosbags
```

兼容系统：
- Ubuntu 20.04 / 22.04 / 24.04
- ROS1 Noetic / ROS2 Humble / ROS2 Jazzy（均非必需）

## 使用方法

### ROS2 db3 → ROS1 bag

```bash
python3 scripts/db3_to_bag.py <input.db3> [output.bag]
```

**示例：**
```bash
# 输入: rosbag2_2026_02_06-09_37_00_0.db3
# 输出: rosbag_2026_02_06-09_37_00_0.bag
python3 scripts/db3_to_bag.py /path/to/rosbag2_2026_02_06-09_37_00_0.db3
```

### ROS1 bag → ROS2 db3

```bash
python3 scripts/bag_to_db3.py <input.bag> [output_name]
```

**示例：**
```bash
# 输入: rosbag_2026_02_06-09_37_00_0.bag
# 输出: rosbag2_2026_02_06-09_37_00_0/ (目录)
#       └── rosbag2_2026_02_06-09_37_00_0.db3 + metadata.yaml
python3 scripts/bag_to_db3.py /path/to/rosbag_2026_02_06-09_37_00_0.bag
```

指定输出名（可带或不带 `.db3` 后缀，均生成同名目录）：
```bash
# 以下两条命令等价，均生成目录 output/，内含 output.db3 与 metadata.yaml
python3 scripts/bag_to_db3.py input.bag output
python3 scripts/bag_to_db3.py input.bag output.db3
```

## 转换示例输出

```
Converting out.bag to 1

Bag duration: 17.28 seconds
Message count: 10887

Topics found:
  /livox/imu_10_5_10_101: sensor_msgs/msg/Imu (3456 messages)
  /livox/imu_10_5_10_102: sensor_msgs/msg/Imu (3456 messages)
  /livox/imu_10_5_10_103: sensor_msgs/msg/Imu (3456 messages)
  /livox/lidar_10_5_10_101: livox_ros_driver2/msg/CustomMsg (173 messages)
  /livox/lidar_10_5_10_102: livox_ros_driver2/msg/CustomMsg (173 messages)
  /livox/lidar_10_5_10_103: livox_ros_driver2/msg/CustomMsg (173 messages)
Processing message 1/10887...
Processing message 1000/10887...
...

Conversion complete! Output saved to: 1
Output file size: 202.31 MB
```

## 许可证

MIT License
