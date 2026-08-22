# Controllers

`FollowPath` (Regulated Pure Pursuit, RPP) is the default controller.
`FollowPathGraceful` (Graceful Controller) is registered next to it in
`params/nav2_params.yaml` so that the two can be compared on the same route.
Both use the same speed limits (cruise 0.1 m/s, 0.03 m/s on the final
approach, 2.0 rad/s in place). 0.03 m/s is the slowest the cube can drive:
its motor takes speed values of 8 and up (about 0.0225 m/s), and a slower
command stops the wheels, so the approach speed and the in-place turn
(`rotate_to_heading_angular_vel` for RPP, `v_angular_min_in_place` for
Graceful) are kept above that.

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

## Hardware comparison (A4 mat)

Measured with one cube (toio-a7D) on the A4 play mat, nav2 1.3.12, with the
parameters in `params/nav2_params.yaml`. The route is five `NavigateToPose`
legs around the mat with 90° heading changes, (0.06, -0.06) → (0.24, -0.06)
→ (0.24, -0.15) → (0.06, -0.15) → (0.06, -0.06), followed by a zigzag
`NavigateThroughPoses`. `/toio/pose` (50 Hz) is compared with the first
`/plan` of each goal.

| | RPP `FollowPath` | Graceful `FollowPathGraceful` |
|:---|:---|:---|
| 5 legs, total time | **22.7 s** | 33.1 s |
| final position error, mean / max | 3.5 / 5.2 mm | 3.9 / 5.2 mm |
| cross-track error vs `/plan`, mean / worst p95 | **2.6 / 7.9 mm** | 3.0 / 8.8 mm |
| final yaw error, mean / max (5.0 rad/s turns, 0.1 rad tolerance) | 20° / 26° | 10° / 12° |
| final yaw error, mean / max (2.0 rad/s turns, 0.15 rad tolerance) | 4° / 6° | **3° / 6°** |
| zigzag: time, cross-track mean / max | 5.0 s, 2.7 / 6.1 mm | 4.8 s, 3.9 / 7.4 mm |

All goals succeeded with both. RPP is about a third faster and tracks the
path slightly better; with the fixed 0.1 m lookahead the corner cutting is
gone (at most 6 mm off the path at the zigzag corners). RPP stays the
default.

### Settling on the goal heading

With the first parameter set both controllers ended 10-26° off the goal
heading although `yaw_goal_tolerance` was 0.1 rad. The cube keeps turning for
90-110 ms after the stop command (BLE latency, measured with a cmd_vel step):
an in-place turn overshoots by 28° at 5.0 rad/s, 13° at 2.5 rad/s and 9° at
2.0 rad/s. The goal checker succeeds the moment the heading enters the band,
so the final error is roughly the overshoot minus the tolerance.

| RPP, same route | final yaw error, mean / max | 5 legs |
|:---|:---|:---|
| 5.0 rad/s, tolerance 0.1 rad | 20° / 26° | 22.7 s |
| 2.5 rad/s, tolerance 0.1 rad | 6° / 10° | 20.1 s |
| 2.0 rad/s, tolerance 0.1 rad | 5° / 8° | 22.3 s |
| **2.0 rad/s, tolerance 0.15 rad** | **4° / 6°** | 20.5 s |

`rotate_to_heading_angular_vel` (RPP) and `v_angular_min_in_place`
(Graceful) are therefore 2.0 rad/s and `yaw_goal_tolerance` 0.15 rad, which
lands the cube within the tolerance with errors on both sides of zero. 2.0
rad/s is close to the slowest in-place turn the cube can make (about 1.7
rad/s, see below), so there is little room to go slower.

Two things that do not work on this cube, found the hard way:

- An approach speed of 0.02 m/s (1 mm per step) stops the cube: its motor
  takes speed values of 8 and up (about 0.0225 m/s) and 0.02 m/s maps to 7.
  Hence 0.03 m/s for `min_approach_linear_velocity` and `v_linear_min`.
- Graceful's default `v_angular_min_in_place` (0.25 rad/s) leaves the
  initial rotation stalled for the same reason (0.017 m/s per wheel), hence
  2.0 rad/s.
