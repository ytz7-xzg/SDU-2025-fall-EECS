import os
labPath = os.getcwd()
from sys import path
if not labPath in path:
    path.append(labPath)
print 'setting labPath to', labPath

import math
import lib601.util as util
import lib601.sm as sm
import lib601.gfx as gfx
from soar.io import io

# 确保导入了所有需要的模块
import dynamicMoveToPointSkeleton
reload(dynamicMoveToPointSkeleton)
import ffSkeleton
reload(ffSkeleton)
from secretMessage import secret

# 将 verbose 设置为 False 以获得更清晰的输出
verbose = True

# 定义路径点
squarePoints = [util.Point(0.5, 0.5), util.Point(0.0, 1.0),
                util.Point(-0.5, 0.5), util.Point(0.0, 0.0)]

SDU_Dot_list = [util.Point(0.1, 0.2),util.Point(0.3,0.8),
util.Point(0.5,0.3),util.Point(0.8,1.2),util.Point(1.1,0.3), util.Point(1.3, 0.8),util.Point(1.5,
0.2)]# ==========================================================
# Checkoff 3 的核心逻辑
# ==========================================================

# 1. 定义判断条件：前方是否有障碍物
isObstacle = lambda inp: min(inp.sonars[3], inp.sonars[4]) < 0.3

# 2. 定义“停止”状态机
stopMachine = sm.Constant(io.Action())

# 3. 定义“正常图形跟随”状态机 (与Checkoff 2相同)
goalGenerator = ffSkeleton.FollowFigure(SDU_Dot_list)
figureFollower = sm.Cascade(sm.Parallel(goalGenerator, sm.Wire()),
                            dynamicMoveToPointSkeleton.DynamicMoveToPoint())

# 4. 使用 sm.Switch 组合最终的大脑
#    如果 isObstacle 为 True, 执行 stopMachine
#    如果 isObstacle 为 False, 执行 figureFollower
# mySM = sm.Cascade(sm.Parallel(sm.Constant(util.Point(1.0, 0.5)), sm.Wire()),
#                    dynamicMoveToPointSkeleton.DynamicMoveToPoint())
mySM = sm.Switch(isObstacle, stopMachine, figureFollower)

######################################################################
###
###          Brain methods
###
######################################################################

def setup():
    robot.gfx = gfx.RobotGraphics(drawSlimeTrail = True)
    robot.behavior = mySM

def brainStart():
    robot.behavior.start(traceTasks = robot.gfx.tasks(),
                         verbose = verbose)

def step():
    robot.behavior.step(io.SensorInput()).execute()
    io.done(robot.behavior.isDone())

def brainStop():
    pass

def shutdown():
    pass