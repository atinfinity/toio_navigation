# Multi-robot navigation

`toio_multi_navigation.launch.py` launches one nav2 stack per robot.
The robot list defaults to `toio1,toio2` and can be changed with the
`robots` argument (e.g. `robots:=toio1,toio2,toio3`); every robot gets
all the other robots as peers for `peer_robot_costmap_publisher`.
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

## Avoidance of the peer robots

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

The node is launched as part of `navigation.launch.py`. It can also be
launched standalone (e.g. for other robots):

```bash
ros2 launch toio_navigation peer_robot_costmap_publisher.launch.py namespace:=toio1 peer_base_frames:=toio2/base_footprint
```
