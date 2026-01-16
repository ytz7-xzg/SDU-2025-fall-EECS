# -*- coding: utf-8 -*-
import lib601.sm as sm
import lib601.util as util

# ================================================
# 全局常量定义
# ================================================
# 定义一个距离阈值，当机器人与目标点的距离小于此值时，认为“已到达”
WAYPOINT_EPSILON = 0.1

class FollowFigure(sm.SM):
    """
    一个状态机，接收一个路点列表。
    它按顺序输出这些点，直到机器人接近当前目标点后，再输出下一个。
    """
    def __init__(self, waypoints):
        """
        waypoints: 一个 util.Point 对象的列表。
        """
        self.waypoints = waypoints
        # 初始状态是第一个路点的索引：0
        self.startState = 0

    def getNextValues(self, state, inp):
        """
        state: 当前目标路点在 self.waypoints 列表中的索引。
        inp:   io.SensorInput 对象，包含里程计信息。
        """
        # 1. 根据当前状态(索引)，获取当前的目标点
        currentTarget = self.waypoints[state]

        # 2. 从传感器输入中获取机器人当前的位置点
        robotPoint = inp.odometry.point()

        # 3. 检查机器人是否已经接近当前目标点
        is_near_target = robotPoint.isNear(currentTarget, WAYPOINT_EPSILON)

        # 4. 决定下一个状态 (下一个目标点的索引)
        if is_near_target:
            # 如果已到达，下一个状态是下一个点的索引
            # 使用 min() 来确保索引不会超出列表范围，如果已是最后一个点，则保持不变
            next_state = min(state + 1, len(self.waypoints) - 1)
        else:
            # 如果还未到达，下一个状态保持不变
            next_state = state

        # 5. 确定输出：输出的永远是当前正在追逐的目标点
        output = currentTarget

        # 6. 返回 (下一个状态, 当前输出)
        return (next_state, output)