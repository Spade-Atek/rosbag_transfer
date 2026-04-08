#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
from rosbags.rosbag1 import Writer as Writer1
from rosbags.rosbag2 import Reader as Reader2
from rosbags.typesys import get_types_from_msg, get_typestore, Stores

CUSTOM_POINT_MSG = """
uint32 offset_time
float32 x
float32 y
float32 z
uint8 reflectivity
uint8 tag
uint8 line
"""

CUSTOM_MSG_MSG = """
std_msgs/Header header
uint64 timebase
uint32 point_num
uint8 lidar_id
uint8[3] rsvd
CustomPoint[] points
"""

typestore_ros1 = get_typestore(Stores.ROS1_NOETIC)
typestore_ros2 = get_typestore(Stores.ROS2_HUMBLE)

typestore_ros1.register(get_types_from_msg(CUSTOM_POINT_MSG, 'livox_ros_driver2/CustomPoint'))
typestore_ros1.register(get_types_from_msg(CUSTOM_MSG_MSG, 'livox_ros_driver2/CustomMsg'))

typestore_ros2.register(get_types_from_msg(CUSTOM_POINT_MSG, 'livox_ros_driver2/msg/CustomPoint'))
typestore_ros2.register(get_types_from_msg(CUSTOM_MSG_MSG, 'livox_ros_driver2/msg/CustomMsg'))

Time = typestore_ros1.types['builtin_interfaces/msg/Time']
Header = typestore_ros1.types['std_msgs/msg/Header']
Quaternion = typestore_ros1.types['geometry_msgs/msg/Quaternion']
Vector3 = typestore_ros1.types['geometry_msgs/msg/Vector3']
Imu = typestore_ros1.types['sensor_msgs/msg/Imu']
CustomPoint = typestore_ros1.types['livox_ros_driver2/msg/CustomPoint']
CustomMsg = typestore_ros1.types['livox_ros_driver2/msg/CustomMsg']

def convert_imu_ros2_to_ros1(imu2_msg):
    imu1_msg = Imu(
        header=Header(
            seq=0,
            stamp=Time(
                sec=imu2_msg.header.stamp.sec,
                nanosec=imu2_msg.header.stamp.nanosec,
            ),
            frame_id=imu2_msg.header.frame_id,
        ),
        orientation=Quaternion(
            x=imu2_msg.orientation.x,
            y=imu2_msg.orientation.y,
            z=imu2_msg.orientation.z,
            w=imu2_msg.orientation.w,
        ),
        orientation_covariance=np.array(imu2_msg.orientation_covariance, dtype=np.float64),
        angular_velocity=Vector3(
            x=imu2_msg.angular_velocity.x,
            y=imu2_msg.angular_velocity.y,
            z=imu2_msg.angular_velocity.z,
        ),
        angular_velocity_covariance=np.array(imu2_msg.angular_velocity_covariance, dtype=np.float64),
        linear_acceleration=Vector3(
            x=imu2_msg.linear_acceleration.x,
            y=imu2_msg.linear_acceleration.y,
            z=imu2_msg.linear_acceleration.z,
        ),
        linear_acceleration_covariance=np.array(imu2_msg.linear_acceleration_covariance, dtype=np.float64),
    )
    return imu1_msg

def convert_custom_msg_ros2_to_ros1(msg2):
    points = []
    for p in msg2.points:
        pt = CustomPoint(
            offset_time=p.offset_time,
            x=p.x,
            y=p.y,
            z=p.z,
            reflectivity=p.reflectivity,
            tag=p.tag,
            line=p.line,
        )
        points.append(pt)
    
    msg1 = CustomMsg(
        header=Header(
            seq=0,
            stamp=Time(
                sec=msg2.header.stamp.sec,
                nanosec=msg2.header.stamp.nanosec,
            ),
            frame_id=msg2.header.frame_id,
        ),
        timebase=msg2.timebase,
        point_num=msg2.point_num,
        lidar_id=msg2.lidar_id,
        rsvd=np.array(msg2.rsvd, dtype=np.uint8),
        points=points,
    )
    return msg1

def convert_db3_to_ros1(db3_path, output_path=None):
    if output_path is None:
        db3_name = os.path.basename(db3_path)
        bag_name = db3_name.replace('.db3', '.bag').replace('rosbag2', 'rosbag')
        output_dir = os.path.dirname(db3_path)
        if not os.access(output_dir, os.W_OK):
            output_dir = os.getcwd()
            print(f"Warning: Source directory is not writable, saving to: {output_dir}")
        output_path = os.path.join(output_dir, bag_name)
    
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"Removed existing file: {output_path}")
    
    print(f"Converting {db3_path} to {output_path}")
    
    with Reader2(db3_path) as reader:
        print(f"\nBag duration: {reader.duration / 1e9:.2f} seconds")
        print(f"Message count: {reader.message_count}")
        print("\nTopics found:")
        for conn in reader.connections:
            print(f"  {conn.topic}: {conn.msgtype} ({conn.msgcount} messages)")
        
        with Writer1(output_path) as writer:
            conn_map = {}
            for conn in reader.connections:
                conn_map[conn.id] = writer.add_connection(
                    conn.topic,
                    conn.msgtype,
                    typestore=typestore_ros1
                )
            
            processed = 0
            total = reader.message_count
            
            for conn, timestamp, rawdata in reader.messages():
                processed += 1
                if processed % 1000 == 0 or processed == 1:
                    print(f"Processing message {processed}/{total}...")
                
                if conn.msgtype == 'sensor_msgs/msg/Imu':
                    msg2 = typestore_ros2.deserialize_cdr(rawdata, conn.msgtype)
                    msg1 = convert_imu_ros2_to_ros1(msg2)
                    serialized = typestore_ros1.serialize_ros1(msg1, conn.msgtype)
                elif conn.msgtype == 'livox_ros_driver2/msg/CustomMsg':
                    msg2 = typestore_ros2.deserialize_cdr(rawdata, conn.msgtype)
                    msg1 = convert_custom_msg_ros2_to_ros1(msg2)
                    serialized = typestore_ros1.serialize_ros1(msg1, conn.msgtype)
                else:
                    serialized = rawdata
                
                writer.write(conn_map[conn.id], timestamp, serialized)
    
    print(f"\nConversion complete! Output saved to: {output_path}")
    print(f"Output file size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python db3_to_bag.py <input.db3> [output.bag]")
        sys.exit(1)
    
    db3_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(db3_path):
        print(f"Error: File not found: {db3_path}")
        sys.exit(1)
    
    convert_db3_to_ros1(db3_path, output_path)
