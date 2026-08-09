# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.actions import PushRosNamespace
from launch_ros.actions import SetParameter
from launch_ros.descriptions import ParameterFile
from launch_ros.parameter_descriptions import ParameterValue
from nav2_common.launch import ReplaceString, RewrittenYaml


def generate_launch_description():
    # Get the launch directory
    toio_navigation_dir = get_package_share_directory('toio_navigation')

    namespace = LaunchConfiguration('namespace')
    frame_prefix = LaunchConfiguration('frame_prefix')
    peer_namespace = LaunchConfiguration('peer_namespace')
    peer_frame_prefix = LaunchConfiguration('peer_frame_prefix')
    peer_frame_prefixes = LaunchConfiguration('peer_frame_prefixes')
    peer_footprint_size = LaunchConfiguration('peer_footprint_size')
    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')
    bt_file = LaunchConfiguration('bt_file')
    use_respawn = LaunchConfiguration('use_respawn')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config_file = LaunchConfiguration('rviz_config')
    log_level = LaunchConfiguration('log_level')

    rviz_config_dir = os.path.join(toio_navigation_dir, 'rviz')

    # toio has no range sensor and no dock, so the sensor/dock-dependent
    # servers of the standard nav2 bringup (collision_monitor without an
    # existing observation source, docking_server, route_server without a
    # graph, and velocity_smoother) are not launched: with two robots on
    # one machine every extra server costs a process per robot.
    lifecycle_nodes = [
        'map_server',
        'controller_server',
        'smoother_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'waypoint_follower',
    ]

    # The robots are separated by the shared /tf with frame_prefix
    # (e.g. map -> toio1/center) following the convention of toio_ros2 and
    # toio_gazebo, so /tf is NOT remapped into the namespace here.
    # Create our own temporary YAML files that include substitutions
    param_substitutions = {'autostart': autostart}

    params_file_with_prefix = ReplaceString(
        source_file=params_file,
        replacements={
            '<frame_prefix>': frame_prefix,
            '<robot_namespace>': PythonExpression(
                ["'' if '", namespace, "' == '' else '/' + '", namespace, "'"]),
        },
    )

    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file_with_prefix,
            root_key=namespace,
            param_rewrites=param_substitutions,
            convert_types=True,
        ),
        allow_substs=True,
    )

    stdout_linebuf_envvar = SetEnvironmentVariable(
        'RCUTILS_LOGGING_BUFFERED_STREAM', '1'
    )

    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace', default_value='', description='Top-level namespace'
    )

    declare_frame_prefix_cmd = DeclareLaunchArgument(
        'frame_prefix',
        default_value='',
        description='Prefix of the TF frames (e.g. "toio1/")',
    )

    declare_peer_namespace_cmd = DeclareLaunchArgument(
        'peer_namespace',
        default_value='',
        description='Namespace of the peer robot shown in RViz '
                    '(used by rviz/nav2_multi.rviz)',
    )

    declare_peer_frame_prefix_cmd = DeclareLaunchArgument(
        'peer_frame_prefix',
        default_value='',
        description='TF frame prefix of the peer robot shown in RViz '
                    '(used by rviz/nav2_multi.rviz)',
    )

    declare_peer_frame_prefixes_cmd = DeclareLaunchArgument(
        'peer_frame_prefixes',
        default_value='',
        description='Comma-separated TF frame prefixes of ALL peer robots '
                    '(e.g. "toio2/,toio3/") for peer_robot_costmap_publisher. '
                    'Empty: fall back to the single peer_frame_prefix',
    )

    declare_peer_footprint_size_cmd = DeclareLaunchArgument(
        'peer_footprint_size',
        default_value='0.032',
        description='Edge length (m) of the square footprint that '
                    'peer_robot_costmap_publisher paints for each peer '
                    'robot. Larger values add avoidance margin (e.g. an '
                    'external traffic authority may want 0.06)',
    )

    declare_rviz_config_cmd = DeclareLaunchArgument(
        'rviz_config',
        default_value=os.path.join(rviz_config_dir, 'nav2.rviz'),
        description='Full path to the RViz config file template',
    )

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map', default_value='', description='Full path to map yaml file to load'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true',
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(toio_navigation_dir, 'params', 'nav2_params.yaml'),
        description='Full path to the ROS2 parameters file to use for all launched nodes',
    )

    declare_bt_file_cmd = DeclareLaunchArgument(
        'bt_file',
        default_value=os.path.join(
            toio_navigation_dir, 'behavior_trees',
            'navigate_to_pose_w_replanning_and_recovery.xml'),
        description='Full path to the BT XML file',
    )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack',
    )

    declare_use_respawn_cmd = DeclareLaunchArgument(
        'use_respawn',
        default_value='False',
        description='Whether to respawn if a node crashes. Applied when composition is disabled.',
    )

    declare_use_rviz_cmd = DeclareLaunchArgument(
        'use_rviz', default_value='True', description='Whether to start RViz'
    )

    declare_log_level_cmd = DeclareLaunchArgument(
        'log_level', default_value='info', description='log level'
    )

    load_nodes = GroupAction(
        actions=[
            PushRosNamespace(
                condition=IfCondition(
                    PythonExpression(["'", namespace, "' != ''"])),
                namespace=namespace),
            SetParameter('use_sim_time', use_sim_time),
            Node(
                package='nav2_map_server',
                executable='map_server',
                name='map_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params, {'yaml_filename': map_yaml_file}],
                arguments=['--ros-args', '--log-level', log_level],
            ),
            Node(
                package='nav2_controller',
                executable='controller_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
            ),
            Node(
                package='nav2_smoother',
                executable='smoother_server',
                name='smoother_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
            ),
            Node(
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
            ),
            Node(
                package='nav2_behaviors',
                executable='behavior_server',
                name='behavior_server',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
            ),
            Node(
                package='nav2_bt_navigator',
                executable='bt_navigator',
                name='bt_navigator',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params, {'default_nav_to_pose_bt_xml': bt_file}],
                arguments=['--ros-args', '--log-level', log_level],
            ),
            Node(
                package='nav2_waypoint_follower',
                executable='waypoint_follower',
                name='waypoint_follower',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[configured_params],
                arguments=['--ros-args', '--log-level', log_level],
            ),
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_navigation',
                output='screen',
                arguments=['--ros-args', '--log-level', log_level],
                parameters=[{'autostart': autostart}, {'node_names': lifecycle_nodes}],
            ),
            Node(
                package='toio_navigation',
                executable='peer_robot_costmap_publisher',
                name='peer_robot_costmap_publisher',
                output='screen',
                respawn=use_respawn,
                respawn_delay=2.0,
                parameters=[
                    configured_params,
                    # peer_frame_prefixes (list form, for 3+ robots) takes
                    # precedence over the single peer_frame_prefix
                    {'peer_base_frames': PythonExpression(
                        ["','.join(p.strip() + 'base_footprint' "
                         "for p in '", peer_frame_prefixes,
                         "'.split(',') if p.strip()) if '",
                         peer_frame_prefixes, "' != '' else ('",
                         peer_frame_prefix, "base_footprint' if '",
                         peer_namespace, "' != '' else '')"])},
                    {'footprint_length': ParameterValue(
                        peer_footprint_size, value_type=float),
                     'footprint_width': ParameterValue(
                        peer_footprint_size, value_type=float)},
                ],
                arguments=['--ros-args', '--log-level', log_level],
            ),
        ],
    )

    # <robot_namespace> in the rviz config is expanded to '' (default) or
    # '/<namespace>' so that the same config works for both cases.
    # <tf_frame_prefix> is the frame_prefix without the trailing slash
    # because the RobotModel display joins it with the link name by '/'.
    namespaced_rviz_config_file = ReplaceString(
        source_file=rviz_config_file,
        replacements={
            '<robot_namespace>': PythonExpression(
                ["'' if '", namespace, "' == '' else '/' + '", namespace, "'"]),
            '<tf_frame_prefix>': PythonExpression(
                ["'", frame_prefix, "'.rstrip('/')"]),
            '<peer_robot_namespace>': PythonExpression(
                ["'' if '", peer_namespace, "' == '' else '/' + '",
                 peer_namespace, "'"]),
            '<peer_tf_frame_prefix>': PythonExpression(
                ["'", peer_frame_prefix, "'.rstrip('/')"]),
        },
    )

    rviz2_node = Node(
        condition=IfCondition(use_rviz),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        namespace=namespace,
        arguments=['-d', namespaced_rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen')

    # Create the launch description and populate
    ld = LaunchDescription()

    # Set environment variables
    ld.add_action(stdout_linebuf_envvar)

    # Declare the launch options
    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_frame_prefix_cmd)
    ld.add_action(declare_peer_namespace_cmd)
    ld.add_action(declare_peer_frame_prefix_cmd)
    ld.add_action(declare_peer_frame_prefixes_cmd)
    ld.add_action(declare_peer_footprint_size_cmd)
    ld.add_action(declare_rviz_config_cmd)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_bt_file_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_use_respawn_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_log_level_cmd)
    # Add the actions to launch all of the navigation nodes
    ld.add_action(load_nodes)
    ld.add_action(rviz2_node)

    return ld
