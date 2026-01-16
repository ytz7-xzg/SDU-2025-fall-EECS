# -*- coding: utf-8 -*-
import math
import lib601.util as util
import lib601.sm as sm
import lib601.gfx as gfx
from soar.io import io

# ================================================
# 全局常量定义 (Global Constants Definition)
# ================================================

# 误差控制器
GLOBAL_ERROR = 0.050
# --- 行为控制常量 ---
TARGET_WALL_DISTANCE = 0.4
FORWARD_SPEED = 0.1              # <--- 遵从您的要求，保持不变
TURN_SPEED_HARD = 0.3            # <--- 修改: 从 0.15 大幅提高
TURN_SPEED_LIGHT = 0.05          # <--- 修改: 从 0.05 大幅提高
ALIGN_DELAY_STEPS = 1            # <--- 修改: 从 10 大幅减少，以适配新的转向速度

# --- 传感器阈值常量 ---
FRONT_OBSTACLE_THRESHOLD = 0.35
INNER_CORNER_THRESHOLD = 0.2
OUTER_CORNER_THRESHOLD = 1.0
RIGHT_DISTANCE_CHANGE_THRESHOLD = 0.3
WALL_PROXIMITY_THRESHOLD = 0.7

# --- P-控制器增益常量 (Proportional Controller Gains) ---
K_DISTANCE = 1.2
K_ANGLE = 1.5

# --- 核心稳定逻辑的关键参数 ---
MAX_ANGLE_RVEL_COMPONENT = TURN_SPEED_LIGHT


class MySMClass(sm.SM):
    """
    定义了机器人大脑的核心状态机。
    """

    def __init__(self):
        """
        状态机初始化函数。
        """
        self.startState = 'DrivingForward'
        self.last_right_distance = float('inf')
        self.align_delay_counter = 0
        self.last_driving_right_distance = float('inf')

    def getNextValues(self, state, inp):
        """
        这是状态机的大脑核心，每个时间步都会被调用一次。
        """
        sonars = inp.sonars
        front_distance = min(sonars[3], sonars[4])
        right_distance_far = sonars[7]
        right_distance_near = sonars[6]
        left_distance_far = sonars[0]

        fvel = 0.0
        rvel = 0.0
        next_state = state

        if state == 'DrivingForward':
            change_in_right_distance = right_distance_far - self.last_driving_right_distance

            if front_distance < FRONT_OBSTACLE_THRESHOLD or min(sonars[6],sonars[7]) < 0.35:
                next_state = 'AligningOnWall'
                self.last_right_distance = float('inf')
                self.align_delay_counter = 0

            elif change_in_right_distance > RIGHT_DISTANCE_CHANGE_THRESHOLD and \
                    self.last_driving_right_distance < WALL_PROXIMITY_THRESHOLD:
                next_state = 'TurningOuterCorner'

            else:
                fvel = FORWARD_SPEED

            self.last_driving_right_distance = right_distance_far

        elif state == 'AligningOnWall':
            if self.align_delay_counter > 0:
                self.align_delay_counter -= 1
                print(self.align_delay_counter)
                next_state = 'AligningOnWall'
                fvel = 0.0
                rvel = TURN_SPEED_HARD

                if self.align_delay_counter == 0:
                    print("Timer Finished")
                    next_state = 'DrivingForward'


            current_right_distance = right_distance_far
            if current_right_distance > self.last_right_distance and self.last_right_distance != float('inf'):
                self.align_delay_counter = ALIGN_DELAY_STEPS
                print("Timer Started")
                next_state = 'DrivingForward'
                fvel = 0.0
                rvel = TURN_SPEED_HARD
            else:
                next_state = 'AligningOnWall'
                fvel = 0.0
                rvel = TURN_SPEED_HARD
                self.last_right_distance = current_right_distance

        elif state == 'TurningOuterCorner':
            if front_distance < FRONT_OBSTACLE_THRESHOLD * 1.5:
                next_state = 'AligningOnWall'
                self.last_right_distance = float('inf')
                self.align_delay_counter = 0
            else:
                next_state = 'TurningOuterCorner'
                fvel = FORWARD_SPEED * 0.8
                rvel = -TURN_SPEED_LIGHT * 2

        fvel = util.clip(fvel, -FORWARD_SPEED, FORWARD_SPEED)
        rvel = util.clip(rvel, -TURN_SPEED_HARD, TURN_SPEED_HARD)

        print("Current State: %s" % state)
        print("Front Distance: %s" % front_distance)
        print("Right Distance: %s" % right_distance_far)
        return (next_state, io.Action(fvel=fvel, rvel=rvel))


mySM = MySMClass()
mySM.name = 'brainSM'


######################################################################
###
###          Brain methods (Soar的标准模板)
###
######################################################################
def setup():
    robot.gfx = gfx.RobotGraphics(drawSlimeTrail=False, sonarMonitor=False)
    robot.behavior = mySM


def brainStart():
    robot.behavior.start(traceTasks=robot.gfx.tasks())


def step():
    inp = io.SensorInput()
    action = robot.behavior.step(inp)
    action.execute()
    io.done(robot.behavior.isDone())


def brainStop():
    pass


def shutdown():
    pass
