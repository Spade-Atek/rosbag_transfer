#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import shutil
from rosbags.rosbag1 import Reader as Reader1
from rosbags.rosbag2 import Writer as Writer2
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

CUSTOM_POINT_DEF = get_types_from_msg(CUSTOM_POINT_MSG, 'livox_ros_driver2/msg/CustomPoint')
CUSTOM_MSG_DEF = get_types_from_msg(CUSTOM_MSG_MSG, 'livox_ros_driver2/msg/CustomMsg')

typestore = get_typestore(Stores.ROS2_HUMBLE)
typestore.register(CUSTOM_POINT_DEF)
typestore.register(CUSTOM_MSG_DEF)

def convert_bag_to_db3(bag_path, output_path=None):
    if output_path is None:
        bag_name = os.path.basename(bag_path)
        db3_name = bag_name.replace('.bag', '').replace('rosbag', 'rosbag2')
        output_dir = os.path.dirname(bag_path)
        if not os.access(output_dir, os.W_OK):
            output_dir = os.getcwd()
            print(f"Warning: Source directory is not writable, saving to: {output_dir}")
        output_path = os.path.join(output_dir, db3_name)
    else:
        # rosbags Writer2 always creates a directory and names the inner .db3
        # file as `{dir_name}.db3`. If user passes a name ending with `.db3`,
        # strip the suffix to avoid producing `name.db3.db3`.
        if output_path.endswith('.db3'):
            output_path = output_path[:-len('.db3')]

    if os.path.exists(output_path):
        if os.path.isdir(output_path):
            shutil.rmtree(output_path)
        else:
            os.remove(output_path)
        print(f"Removed existing path: {output_path}")

    print(f"Converting {bag_path} to {output_path}")

    with Reader1(bag_path) as reader:
        print(f"\nBag duration: {reader.duration / 1e9:.2f} seconds")
        print(f"Message count: {reader.message_count}")
        print("\nTopics found:")
        for topic, info in reader.topics.items():
            print(f"  {topic}: {info.msgtype} ({info.msgcount} messages)")

        with Writer2(output_path, version=Writer2.VERSION_LATEST) as writer:
            conn_map = {}
            for conn in reader.connections:
                conn_map[conn.id] = writer.add_connection(
                    conn.topic,
                    conn.msgtype,
                    typestore=typestore
                )

            processed = 0
            total = reader.message_count

            for conn, timestamp, rawdata in reader.messages():
                processed += 1
                if processed % 1000 == 0 or processed == 1:
                    print(f"Processing message {processed}/{total}...")

                writer.write(conn_map[conn.id], timestamp, rawdata)

    total_size = sum(
        os.path.getsize(os.path.join(dirpath, f))
        for dirpath, _, files in os.walk(output_path) for f in files
    )
    print(f"\nConversion complete! Output saved to: {output_path}")
    print(f"Output file size: {total_size / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python bag_to_db3.py <input.bag> [output_name]")
        sys.exit(1)

    bag_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(bag_path):
        print(f"Error: File not found: {bag_path}")
        sys.exit(1)

    convert_bag_to_db3(bag_path, output_path)
