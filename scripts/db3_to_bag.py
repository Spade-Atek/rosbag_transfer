#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
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

CUSTOM_POINT_DEF = get_types_from_msg(CUSTOM_POINT_MSG, 'livox_ros_driver2/msg/CustomPoint')
CUSTOM_MSG_DEF = get_types_from_msg(CUSTOM_MSG_MSG, 'livox_ros_driver2/msg/CustomMsg')

typestore = get_typestore(Stores.ROS2_HUMBLE)
typestore.register(CUSTOM_POINT_DEF)
typestore.register(CUSTOM_MSG_DEF)

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
                    typestore=typestore
                )
            
            processed = 0
            total = reader.message_count
            
            for conn, timestamp, rawdata in reader.messages():
                processed += 1
                if processed % 1000 == 0 or processed == 1:
                    print(f"Processing message {processed}/{total}...")
                
                writer.write(conn_map[conn.id], timestamp, rawdata)
    
    print(f"\nConversion complete! Output saved to: {output_path}")
    print(f"Output file size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python db3_to_ros1.py <input.db3> [output.bag]")
        sys.exit(1)
    
    db3_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(db3_path):
        print(f"Error: File not found: {db3_path}")
        sys.exit(1)
    
    convert_db3_to_ros1(db3_path, output_path)
