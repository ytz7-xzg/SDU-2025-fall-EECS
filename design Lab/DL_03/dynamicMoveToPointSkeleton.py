# -*- coding: utf-8 -*-
import lib601.sm as sm
import lib601.util as util
import math
import sys  # <--- 修改: 导入sys模块以访问stderr

# Use this line for running in idle
# import lib601.io as io

# Use this line for testing in soar
from soar.io import io

# ================================================
# 全局常量定义
# ================================================

# --- 控制器增益 (K值) ---
K_ROT = 0.7
K_VEL = 0.9

# --- 误差阈值 (Epsilon值) ---
ANGLE_EPS = 0.02
DIST_EPS = 0.005


class DynamicMoveToPoint(sm.SM):
    def getNextValues(self, state, inp):

        assert isinstance(inp, tuple), 'inp should be a tuple'
        assert len(inp) == 2, 'inp should be of length 2'
        assert isinstance(inp[0], util.Point), 'inp[0] should be a Point'

        goalPoint, sensors = inp
        robotPose = sensors.odometry

        # <--- 修改: 将所有 print 改为 print >> sys.stderr, ...
        # 这样做可以强制将输出发送到标准错误流，在实车上更容易被看到
        print >> sys.stderr, "----------- DynamicMoveToPoint: New Step -----------"
        print >> sys.stderr, "Current Robot Pose: x=%.2f, y=%.2f, theta=%.2f" % (robotPose.x, robotPose.y, robotPose.theta)
        print >> sys.stderr, "Current Goal Point: x=%.2f, y=%.2f" % (goalPoint.x, goalPoint.y)

        fvel = 0.0
        rvel = 0.0

        dist_error = robotPose.point().distance(goalPoint)
        print >> sys.stderr, "Calculated Distance Error: %.4f meters" % dist_error

        if dist_error < DIST_EPS:
            fvel = 0.0
            rvel = 0.0
            print >> sys.stderr, "STATE: Goal Reached! Stopping robot."
        else:
            angle_to_goal = robotPose.point().angleTo(goalPoint)
            angle_error = util.fixAnglePlusMinusPi(angle_to_goal - robotPose.theta)
            print >> sys.stderr, "Calculated Angle Error:    %.4f radians" % angle_error

            if abs(angle_error) > ANGLE_EPS:
                fvel = 0.0
                rvel = K_ROT * angle_error
                print >> sys.stderr, "STATE: Angle error is too large. Rotating."
            else:
                fvel = K_VEL * dist_error
                rvel = 0.0
                print >> sys.stderr, "STATE: Aligned with goal. Moving forward."

        print >> sys.stderr, "Output Action: fvel=%.3f, rvel=%.3f" % (fvel, rvel)
        print >> sys.stderr, "-----------------------------------------------------\n"

        return (state, io.Action(fvel=fvel, rvel=rvel))