// Copyright (C) 2025 atinfinity
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// IsPathEndNearGoal: a BT condition that fails when the planned path does
// not end at the goal (issue #28).
//
// NavFn is configured with a 0.05 m tolerance so that a goal blocked by a
// peer robot still gets a plan to a point next to it. The same tolerance
// lets a plan that cannot reach the goal at all - the cube stuck inside the
// inflation layer's inscribed band after cutting a corner - degenerate to
// a path that starts and ends at the robot's own pose. FollowPath then
// "reaches" that path end at once and the navigation reports success 61 mm
// short of the goal (measured on the A4 spiral map). This node sits between
// ComputePathToPose and FollowPath and turns that case into a failure, so
// the recovery subtree and the retry counter see the stall.

#include <cmath>
#include <string>

#include "behaviortree_cpp/bt_factory.h"
#include "behaviortree_cpp/condition_node.h"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav_msgs/msg/path.hpp"
#include "rclcpp/rclcpp.hpp"

namespace toio_navigation
{

class IsPathEndNearGoalCondition : public BT::ConditionNode
{
public:
  IsPathEndNearGoalCondition(const std::string & name, const BT::NodeConfig & conf)
  : BT::ConditionNode(name, conf),
    logger_(rclcpp::get_logger("IsPathEndNearGoal")),
    // The throttle macros keep a reference to the clock between ticks, so
    // it has to outlive the call (a temporary clock crashed bt_navigator).
    clock_(RCL_STEADY_TIME)
  {
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<nav_msgs::msg::Path>("path", "Planned path"),
      BT::InputPort<geometry_msgs::msg::PoseStamped>("goal", "Requested goal"),
      BT::InputPort<double>(
        "tolerance", 0.01,
        "Maximum distance (m) between the end of the path and the goal"),
    };
  }

  BT::NodeStatus tick() override
  {
    nav_msgs::msg::Path path;
    geometry_msgs::msg::PoseStamped goal;
    double tolerance = 0.01;
    if (!getInput("path", path) || !getInput("goal", goal)) {
      RCLCPP_WARN_THROTTLE(
        logger_, clock_, 1000,
        "path or goal input missing");
      return BT::NodeStatus::FAILURE;
    }
    getInput("tolerance", tolerance);

    if (path.poses.empty()) {
      RCLCPP_WARN_THROTTLE(
        logger_, clock_, 1000, "the planned path is empty");
      return BT::NodeStatus::FAILURE;
    }

    const auto & end = path.poses.back().pose.position;
    const auto & target = goal.pose.position;
    const double distance = std::hypot(end.x - target.x, end.y - target.y);
    if (distance > tolerance) {
      RCLCPP_WARN_THROTTLE(
        logger_, clock_, 1000,
        "the planned path ends %.3f m from the goal (tolerance %.3f m, %zu poses): "
        "the goal is not reachable from here",
        distance, tolerance, path.poses.size());
      return BT::NodeStatus::FAILURE;
    }
    return BT::NodeStatus::SUCCESS;
  }

private:
  rclcpp::Logger logger_;
  rclcpp::Clock clock_;
};

}  // namespace toio_navigation

BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<toio_navigation::IsPathEndNearGoalCondition>("IsPathEndNearGoal");
}
