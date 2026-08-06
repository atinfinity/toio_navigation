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
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.descriptions import ParameterFile

from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    toio_navigation_dir = get_package_share_directory('toio_navigation')

    namespace = LaunchConfiguration('namespace')
    peer_base_frames = LaunchConfiguration('peer_base_frames')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Namespace of the robot this publisher belongs to')

    declare_peer_base_frames_cmd = DeclareLaunchArgument(
        'peer_base_frames',
        default_value='',
        description='Comma-separated TF frames of the peer robots '
                    '(e.g. "toio2/base_footprint")')

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(
            toio_navigation_dir, 'params', 'nav2_params.yaml'),
        description='Full path to the ROS2 parameters file to use')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true')

    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key=namespace,
            param_rewrites={},
            convert_types=True,
        ),
        allow_substs=True,
    )

    peer_robot_costmap_publisher_cmd = Node(
        package='toio_navigation',
        executable='peer_robot_costmap_publisher',
        name='peer_robot_costmap_publisher',
        namespace=namespace,
        output='screen',
        parameters=[
            configured_params,
            {'peer_base_frames': peer_base_frames,
             'use_sim_time': use_sim_time},
        ],
    )

    ld = LaunchDescription()
    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_peer_base_frames_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_use_sim_time_cmd)

    ld.add_action(peer_robot_costmap_publisher_cmd)
    return ld
