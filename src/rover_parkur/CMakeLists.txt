cmake_minimum_required(VERSION 3.8)
project(rover_parkur)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(DIRECTORY launch urdf meshes worlds config
  DESTINATION share/${PROJECT_NAME}
)

# Kayar engel Gazebo plugin'i (once plugins/kayar_engel/build altinda derlenmis olmali)
install(FILES plugins/kayar_engel/build/libkayar_engel_plugin.so
  DESTINATION share/${PROJECT_NAME}/plugins
)

install(PROGRAMS
  src/teleop_key.py
  src/teleop_tank.py
  src/skid_steer_controller.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
