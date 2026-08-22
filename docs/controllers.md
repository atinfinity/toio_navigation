# Controllers

`FollowPath` (Regulated Pure Pursuit, RPP) is the default controller.
`FollowPathGraceful` (Graceful Controller) is registered next to it in
`params/nav2_params.yaml` so that the two can be compared on the same route.
Both use the same speed limits (cruise 0.1 m/s, 0.02 m/s on the final
approach, 5.0 rad/s in place).

## Why these two

toio is a 3.2 cm differential-drive cube that only knows its pose from the
play mat, drives at about 0.1 m/s and is commanded over BLE with some latency.
The costmap resolution is 5 mm and the goal tolerance is 5 mm, so tracking the
planned path accurately and stopping cleanly on the goal matter more than
avoiding obstacles locally (the peer robots are handled by replanning, see
[multi_robot.md](multi_robot.md)).

- **RPP** follows the path with a fixed 0.1 m lookahead. It is simple and its
  behaviour is easy to read.
- **Graceful Controller** steers with a smooth pose-following control law
  that converges onto the target pose, which may land the cube on the 5 mm
  goal band more cleanly.
- **MPPI** is not configured: its critics are tuned in metre scale, the
  sampling noise fights the 5 mm tolerance, and it is CPU heavy (several
  nav2 stacks plus RViz instances already load one machine). Consider it only
  if crossings between peer robots get stuck in practice.

## Selecting a controller

At launch (single robot or `toio_multi_navigation.launch.py`):

```bash
ros2 launch toio_navigation navigation.launch.py map:=<MAP_YAML_FILEPATH> controller:=FollowPathGraceful
```

At runtime, through the `ControllerSelector` of the behavior tree. The topic
is transient local, so publish with matching durability:

```bash
ros2 topic pub -1 --qos-durability transient_local /controller_selector std_msgs/msg/String "{data: FollowPathGraceful}"
```

Prefix the topic with the robot namespace for a multi-robot launch
(e.g. `/toio1/controller_selector`). The selection applies from the next
navigation goal.
