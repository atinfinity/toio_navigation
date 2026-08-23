cmake_minimum_required(VERSION 3.10)
project(toio_navigation)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(nav2_common REQUIRED)
find_package(navigation2 REQUIRED)
find_package(rclcpp REQUIRED)
find_package(behaviortree_cpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

nav2_package()

# Behavior tree plugin (issue #28): fails the navigation when the planned
# path does not end at the goal. Loaded by bt_navigator through
# plugin_lib_names in params/nav2_params.yaml.
add_library(toio_navigation_is_path_end_near_goal_bt_node SHARED
  plugins/is_path_end_near_goal_condition.cpp)
target_compile_features(toio_navigation_is_path_end_near_goal_bt_node PUBLIC cxx_std_17)
ament_target_dependencies(toio_navigation_is_path_end_near_goal_bt_node
  rclcpp behaviortree_cpp nav_msgs geometry_msgs)
target_compile_definitions(toio_navigation_is_path_end_near_goal_bt_node
  PRIVATE BT_PLUGIN_EXPORT)
install(TARGETS toio_navigation_is_path_end_near_goal_bt_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  scripts/peer_robot_costmap_publisher
  scripts/lifecycle_starter
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY behavior_trees DESTINATION share/${PROJECT_NAME})
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})
install(DIRECTORY maps DESTINATION share/${PROJECT_NAME})
install(DIRECTORY rviz DESTINATION share/${PROJECT_NAME})
install(DIRECTORY params DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # ament_copyright also requires CONTRIBUTING.md and a LICENSE file in a
  # layout it recognizes; skip it (the copyright test is skipped in
  # toio_ros2 and toio_description as well)
  set(ament_cmake_copyright_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
