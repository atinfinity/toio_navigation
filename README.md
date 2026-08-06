# toio_navigation

## Introduction

`toio_navigation` is ROS 2 package for navigation2 using [toio](https://toio.io/).

https://github.com/user-attachments/assets/14a0fc6d-14b0-4eac-8972-00bf746670f4

## Requirements

### Hardware

- toio Core Cube
- toio play mat
  - Please see <https://toio.github.io/toio-spec/en/docs/hardware_position_id>.

### Software

I checked this package on the following environment.

- Ubuntu 24.04
- ROS 2 Jazzy
- toio.py 1.10.0
- toio_ros2 <https://github.com/atinfinity/toio_ros2>

## Build

```bash
mkdir -p ~/dev_ws/src
cd ~/dev_ws/src
git clone https://github.com/atinfinity/toio_description.git
git clone https://github.com/atinfinity/toio_ros2.git
git clone https://github.com/atinfinity/toio_navigation.git
cd ..
rosdep install -y -i --from-paths src
colcon build --symlink-install
source ~/dev_ws/install/setup.bash
```

## Launch toio_navigation

```bash
ros2 launch toio_navigation navigation.launch.py map:=<MAP_YAML_FILEPATH>
```

An example of command is as follows:

```bash
ros2 launch toio_navigation navigation.launch.py map:=$HOME/dev_ws/src/toio_navigation/maps/toio_a4_map.yaml
```

If you use Gazebo simulator, please add `use_sim_time:=True`.

## Multi-robot navigation

`toio_multi_navigation.launch.py` launches two nav2 stacks for `toio1` and `toio2`.
Each stack is separated by ROS namespace, and the TF frames are separated by
`frame_prefix` (e.g. `toio1/base_link`) on the shared `/tf`. The `map` frame is
shared by all robots.

```bash
ros2 launch toio_navigation toio_multi_navigation.launch.py map:=$HOME/dev_ws/src/toio_navigation/maps/toio_a4_map.yaml
```

If you use Gazebo simulator ([toio_gazebo](https://github.com/atinfinity/toio_gazebo) `toio_multi_simulation.launch.py`), please add `use_sim_time:=True`.

One RViz instance is launched per robot (the windows may overlap at startup —
move one aside). Each RViz shows both robot models on the shared map
(`rviz/nav2_multi.rviz`), while the map, paths and costmaps belong to its own
robot. You can send an independent goal to each robot from its own RViz
("Nav2 Goal" tool), or via CLI:

```bash
ros2 action send_goal /toio1/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 0.20, y: -0.05}}}}"
ros2 action send_goal /toio2/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 0.10, y: -0.15}}}}"
```

To launch a single stack with namespace for your own robot:

```bash
ros2 launch toio_navigation navigation.launch.py namespace:=toio1 frame_prefix:=toio1/ map:=<MAP_YAML_FILEPATH>
```

### Avoidance of the peer robots

`peer_robot_costmap_publisher.py` (launched per robot) looks up the poses of
the peer robots from TF and publishes an `OccupancyGrid` (`peer_robots_costmap`)
which marks each peer as a filled rectangle (rotated by the yaw of the peer)
on top of a copy of the static map. The `peer_robot_layer` (a
`nav2_costmap_2d::StaticLayer`) of the local/global costmaps consumes it, so
the planner and the controller avoid the other robots.

Parameters (`params/nav2_params.yaml`):

- `footprint_length` / `footprint_width`: size of the rectangular footprint
  of a peer robot [m] (default: `0.032`)
- `update_rate`: publish rate [Hz] (default: `10.0`)
- `peer_base_frames`: comma-separated TF frames of the peer robots
  (e.g. `toio2/base_footprint`). Set automatically by
  `toio_multi_navigation.launch.py` via the `peer_namespace` /
  `peer_frame_prefix` arguments.
