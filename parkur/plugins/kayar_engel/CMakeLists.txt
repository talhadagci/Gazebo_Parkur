cmake_minimum_required(VERSION 3.10)
project(kayar_engel_plugin)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(gazebo REQUIRED)
include_directories(${GAZEBO_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})

add_library(kayar_engel_plugin SHARED KayarEngelPlugin.cc)
target_link_libraries(kayar_engel_plugin ${GAZEBO_LIBRARIES})
