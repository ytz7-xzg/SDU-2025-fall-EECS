# -*- coding: utf-8 -*-
import math
import lib601.util as util
import lib601.sm as sm
import lib601.gfx as gfx
from soar.io import io

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

            if front_distance < 0.35 or min(sonars[6],sonars[7]) < 0.25:
                next_state = 'AligningOnWall'
                self.last_right_distance = float('inf')
                self.align_delay_counter = 0

            elif change_in_right_distance > 0.1 and \
                    self.last_driving_right_distance < 0.7:
                next_state = 'TurningOuterCorner'

            else:
                if sonars[7] > 0.4:
                    fvel = 0.1
                    rvel = -0.3 * 3
                fvel = 0.3

            self.last_driving_right_distance = right_distance_far

        elif state == 'AligningOnWall':
            if self.align_delay_counter > 0:
                self.align_delay_counter -= 1
                print(self.align_delay_counter)
                next_state = 'AligningOnWall'
                fvel = 0.0
                rvel = 0.3

                if self.align_delay_counter == 0:
                    print("Timer Finished")
                    next_state = 'DrivingForward'

            else:
                current_right_distance = right_distance_far
                if current_right_distance > self.last_right_distance and self.last_right_distance != float('inf'):
                    self.align_delay_counter = 2
                    print("Timer Started")
                    next_state = 'AligningOnWall'
                    fvel = 0.0
                    rvel = 0.3
                else:
                    next_state = 'AligningOnWall'
                    fvel = 0.0
                    rvel = 0.3
                    self.last_right_distance = current_right_distance

        elif state == 'TurningOuterCorner':
            if front_distance < 0.35 * 1.5:
                next_state = 'AligningOnWall'
                self.last_right_distance = float('inf')
                self.align_delay_counter = 0
            else:
                next_state = 'TurningOuterCorner'
                fvel = 0.3 * 0.5
                rvel = -0.05 * 7

        fvel = util.clip(fvel, -0.3, 0.3)
        rvel = util.clip(rvel, -0.3, 0.3)

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