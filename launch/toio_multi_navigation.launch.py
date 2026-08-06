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
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    toio_navigation_dir = get_package_share_directory('toio_navigation')
    launch_dir = os.path.join(toio_navigation_dir, 'launch')
    # RViz template with an additional RobotModel display for the peer
    # robot, so that each per-robot RViz shows both robots.
    rviz_config_file = os.path.join(
        toio_navigation_dir, 'rviz', 'nav2_multi.rviz')

    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')

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

    # Each include is wrapped in a scoped GroupAction so that its
    # launch_arguments do not leak into this context.
    navigation_toio1 = GroupAction([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(launch_dir, 'navigation.launch.py')),
            launch_arguments={'namespace': 'toio1',
                              'frame_prefix': 'toio1/',
                              'peer_namespace': 'toio2',
                              'peer_frame_prefix': 'toio2/',
                              'map': map_yaml_file,
                              'use_sim_time': use_sim_time,
                              'use_rviz': use_rviz,
                              'rviz_config': rviz_config_file}.items()),
    ])

    navigation_toio2 = GroupAction([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(launch_dir, 'navigation.launch.py')),
            launch_arguments={'namespace': 'toio2',
                              'frame_prefix': 'toio2/',
                              'peer_namespace': 'toio1',
                              'peer_frame_prefix': 'toio1/',
                              'map': map_yaml_file,
                              'use_sim_time': use_sim_time,
                              'use_rviz': use_rviz,
                              'rviz_config': rviz_config_file}.items()),
    ])

    ld = LaunchDescription()
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_rviz_cmd)

    ld.add_action(navigation_toio1)
    ld.add_action(navigation_toio2)
    return ld
