# Copyright (C) 2026 atinfinity
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
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    TimerAction,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource


def navigation_robots(context):
    """
    Create one navigation include per robot listed in the robots argument.

    Every robot gets all the other robots as peers for
    peer_robot_costmap_publisher (peer_frame_prefixes). The single
    peer_namespace / peer_frame_prefix arguments used by the RViz template
    keep pointing at the first peer, so the two-robot RViz layout is
    unchanged.
    """
    toio_navigation_dir = get_package_share_directory('toio_navigation')
    launch_dir = os.path.join(toio_navigation_dir, 'launch')
    # RViz template with an additional RobotModel display for the peer
    # robot, so that each per-robot RViz shows both robots.
    rviz_config_file = os.path.join(
        toio_navigation_dir, 'rviz', 'nav2_multi.rviz')

    robots = [r.strip() for r in
              context.launch_configurations['robots'].split(',') if r.strip()]

    # Starting every robot's ~20 Nav2 nodes at once saturates DDS discovery
    # and the lifecycle managers then time out on their own get_state /
    # change_state calls and abort the bringup (toio_rmf_bringup#57).
    # Start the robots one after the other instead.
    stagger = float(context.launch_configurations['robot_start_stagger'])

    actions = []
    for index, robot in enumerate(robots):
        peers = [r for r in robots if r != robot]
        first_peer = peers[0] if peers else ''
        group = GroupAction([
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(launch_dir, 'navigation.launch.py')),
                launch_arguments={
                    'namespace': robot,
                    'frame_prefix': f'{robot}/',
                    'peer_namespace': first_peer,
                    'peer_frame_prefix':
                        f'{first_peer}/' if first_peer else '',
                    'peer_frame_prefixes':
                        ','.join(f'{p}/' for p in peers),
                    'peer_footprint_size':
                        context.launch_configurations['peer_footprint_size'],
                    'map': context.launch_configurations['map'],
                    'use_sim_time':
                        context.launch_configurations['use_sim_time'],
                    'use_rviz': context.launch_configurations['use_rviz'],
                    'controller':
                        context.launch_configurations['controller'],
                    'use_velocity_smoother':
                        context.launch_configurations['use_velocity_smoother'],
                    'rviz_config': rviz_config_file,
                }.items()),
        ])
        if index == 0 or stagger <= 0.0:
            actions.append(group)
        else:
            actions.append(TimerAction(period=index * stagger, actions=[group]))
    return actions


def generate_launch_description():
    toio_navigation_dir = get_package_share_directory('toio_navigation')

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(
            toio_navigation_dir, 'maps', 'toio_a4_map.yaml'),
        description='Full path to map yaml file to load',
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true',
    )

    declare_use_rviz_cmd = DeclareLaunchArgument(
        'use_rviz',
        default_value='True',
        description='Whether to start RViz (one instance per robot)',
    )

    declare_robots_cmd = DeclareLaunchArgument(
        'robots',
        default_value='toio1,toio2',
        description='Comma-separated list of robot namespaces',
    )

    declare_peer_footprint_size_cmd = DeclareLaunchArgument(
        'peer_footprint_size',
        default_value='0.032',
        description='Edge length (m) of the square footprint painted for '
                    'peer robots (see navigation.launch.py)',
    )

    declare_controller_cmd = DeclareLaunchArgument(
        'controller',
        default_value='FollowPath',
        description='Controller plugin for every robot: "FollowPath" (RPP) '
                    'or "FollowPathGraceful" (see navigation.launch.py)',
    )

    declare_robot_start_stagger_cmd = DeclareLaunchArgument(
        'robot_start_stagger',
        default_value='15.0',
        description='Seconds between the start of consecutive robots\' '
                    'Nav2 stacks. Starting them all at once saturates DDS '
                    'discovery and the lifecycle managers abort their '
                    'bringup (toio_rmf_bringup#57); 0 starts all at once')

    declare_use_velocity_smoother_cmd = DeclareLaunchArgument(
        'use_velocity_smoother',
        default_value='True',
        description='Run velocity_smoother for every robot. False sends the '
                    'controller cmd_vel straight to the cube. One extra node '
                    'per robot; set False to save processes in large fleets '
                    '(see navigation.launch.py)',
    )

    ld = LaunchDescription()
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_robots_cmd)
    ld.add_action(declare_peer_footprint_size_cmd)
    ld.add_action(declare_controller_cmd)
    ld.add_action(declare_use_velocity_smoother_cmd)
    ld.add_action(declare_robot_start_stagger_cmd)

    ld.add_action(OpaqueFunction(function=navigation_robots))
    return ld
