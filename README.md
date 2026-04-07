# ROS2 db3 to ROS1 Bag Converter

将ROS2的db3格式rosbag文件转换为ROS1的bag格式。（Livox Mid360激光雷达采集的数据包）

## 项目结构

```
rosbag_transfer/
├── msg/
│   ├── CustomMsg.msg
│   └── CustomPoint.msg
├── scripts/
│   └── db3_to_bag.py
├── CMakeLists.txt
├── package.xml
└── README.md
```

## 功能特点

- 支持ROS2 db3格式到ROS1 bag格式的转换
- 支持Livox Mid360激光雷达自定义消息类型 (`livox_ros_driver2/msg/CustomMsg`)
- 支持标准IMU消息 (`sensor_msgs/msg/Imu`)
- 自动保留原始时间戳和话题信息

## 依赖

- Python 3.8+
- rosbags库

```bash
pip install rosbags
```

## 使用方法

### 基本用法

```bash
python3 scripts/db3_to_bag.py <input.db3>
```

**示例：**
```bash
# 输入: rosbag2_2026_02_06-09_37_00_0.db3
# 输出: rosbag_2026_02_06-09_37_00_0.bag
python3 scripts/db3_to_bag.py /path/to/rosbag2_2026_02_06-09_37_00_0.db3
```

### 指定输出路径

```bash
python3 scripts/db3_to_bag.py <input.db3> <output.bag>
```

**示例：**
```bash
python3 scripts/db3_to_bag.py input.db3 output.bag
```

## 转换示例输出

```
Converting /path/to/rosbag2_2026_02_06-09_37_00_0.db3 to /path/to/rosbag_2026_02_06-09_37_00_0.bag

Bag duration: 26.80 seconds
Message count: 16885

Topics found:
  /livox/lidar_10_5_10_103: livox_ros_driver2/msg/CustomMsg (268 messages)
  /livox/lidar_10_5_10_101: livox_ros_driver2/msg/CustomMsg (268 messages)
  /livox/imu_10_5_10_103: sensor_msgs/msg/Imu (5360 messages)
  /livox/imu_10_5_10_102: sensor_msgs/msg/Imu (5361 messages)
  /livox/lidar_10_5_10_102: livox_ros_driver2/msg/CustomMsg (268 messages)
  /livox/imu_10_5_10_101: sensor_msgs/msg/Imu (5360 messages)

Processing message 1/16885...
Processing message 1000/16885...
...

Conversion complete! Output saved to: /path/to/rosbag_2026_02_06-09_37_00_0.bag
Output file size: 312.77 MB
```

## 许可证

MIT License
