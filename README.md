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
