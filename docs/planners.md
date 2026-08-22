# Planners

`GridBased` is `nav2_smac_planner::SmacPlanner2D`. `NavFn`
(`nav2_navfn_planner::NavfnPlanner`) is registered next to it for comparison
and can be selected at runtime through the behavior tree's `PlannerSelector`:

```bash
ros2 topic pub -1 --qos-durability transient_local /planner_selector std_msgs/msg/String "{data: NavFn}"
```

## Why not NavFn

NavFn traces its path with at most `4 x (map width in cells)` steps
(`calcPath(size_x * 4)` in nav2's `NavfnPlanner`), about half a cell per
step. On the 60-cell-wide A4 map that is roughly 0.6 m, and on A3 about
0.84 m. A route longer than that comes back truncated, and with
`tolerance: 0.05` the truncated end within 5 cm of the goal was accepted as
the goal. Measured on the A4 spiral map from the outer start (0.073,-0.028):

| goal | NavFn path end | length |
|:---|:---|:---|
| (0.06,-0.098) pocket mouth | at the goal | 0.549 m |
| (0.09,-0.098) | at the goal | 0.562 m |
| (0.13,-0.098) | (0.120,-0.103) | 0.574 m |
| (0.173,-0.098) centre | (0.128,-0.113) | 0.583 m |

Every path stops at about 0.58 m whatever the goal, while the same goals are
planned exactly from inside the pocket. SmacPlanner2D plans the full 0.630 m
route to the centre (real cube, issue #31), and the empty-map route of
[controllers.md](controllers.md) navigates as before (5 legs, 3.7-6.3 mm
final error).

## Tolerance and peer robots

Both planners take `tolerance: 0.05`: when the goal cell is occupied - a
peer robot standing on it, see [multi_robot.md](multi_robot.md) - the plan
ends at the nearest reachable point within 5 cm (checked with a fake peer on
the goal: Smac ends 3 cm above it, NavFn 3 cm beyond it). The behavior
tree's `IsPathEndNearGoal` ([behavior_tree.md](behavior_tree.md)) accepts a
path end only within 0.01 m of the goal, so such a substitute plan is
refused before the cube drives; raise that tolerance to get the old
behaviour of driving next to the peer.
