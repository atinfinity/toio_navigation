# Behavior tree

`behavior_trees/navigate_to_pose_w_replanning_and_recovery.xml` is the nav2
default tree with a few changes for the play mat. `navigation.launch.py`
substitutes the `controller` launch argument into it (see
[controllers.md](controllers.md)).

## Changes from the nav2 default

- **No `Spin` / `BackUp` recovery.** Rotating in place drifts, and a cube
  that leaves the mat loses its Position ID; `BackUp` refuses to run from
  inside a peer's footprint. The comments in the XML have the details.
- **`IsPathEndNearGoal` after `ComputePathToPose`** (this package's BT
  plugin, `plugins/is_path_end_near_goal_condition.cpp`, loaded through
  `bt_navigator.plugin_lib_names`). It fails the tick when the planned path
  does not end within `tolerance` (0.01 m) of the requested goal.

## Why the path end is checked

`GridBased` (NavFn) runs with `tolerance: 0.05` so that a goal blocked by a
peer robot still gets a plan to a point next to it. The same tolerance lets
a goal that cannot be reached at all be replaced by the best reachable point,
and when the cube is stuck inside the inflation layer's inscribed band that
point is its own pose: `ComputePathToPose` returns a two-pose, 3 mm path,
`FollowPath` reaches its end at once and the navigation reports
`Goal succeeded` tens of millimetres from the goal (61 mm on the A4 spiral
map, real cube; issue #28). With the check, that tick fails instead:

```
[IsPathEndNearGoal]: the planned path ends 0.047 m from the goal (tolerance 0.010 m, 207 poses): the goal is not reachable from here
[bt_navigator]: Goal failed
```

so the recovery subtree and the retry counter see the stall, and a goal that
NavFn cannot plan to is refused up front rather than driven towards.

The node has no ROS dependencies beyond the message types and is registered
under the name `IsPathEndNearGoal`:

```xml
<IsPathEndNearGoal path="{path}" goal="{goal}" tolerance="0.01"/>
```

Raise `tolerance` if a deployment wants the old behaviour for goals blocked
by a peer (NavFn substitutes within 0.05 m).

## What the check revealed

With the check in place the A4 spiral centre goal failed from the start
while `GridBased` was NavFn: its path tracing is capped at 4 x (map width in
cells) steps, about 0.6 m on the 60-cell-wide A4 map, and the spiral route
is 0.63 m. The path always stopped 4-5 cm short of the centre and the
tolerance used to hide it. `GridBased` is SmacPlanner2D since #31, which
plans the full route; see [planners.md](planners.md).
