cmake_minimum_required(VERSION 2.8.3)
project(openbot_control)

find_package(catkin REQUIRED)

catkin_package()

install(DIRECTORY config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
