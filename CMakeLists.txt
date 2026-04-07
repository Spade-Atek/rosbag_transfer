cmake_minimum_required(VERSION 3.0.2)
project(rosbag_transfer)

find_package(catkin REQUIRED COMPONENTS
  rosbag
  std_msgs
  sensor_msgs
  message_generation
)

add_message_files(
  FILES
  CustomPoint.msg
  CustomMsg.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS rosbag std_msgs sensor_msgs message_runtime
)

catkin_install_python(PROGRAMS
  scripts/db3_to_bag.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
