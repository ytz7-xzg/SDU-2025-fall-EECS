import math
import lib601.util as util
import lib601.sm as sm
import lib601.gfx as gfx
from soar.io import io

# 将这部分代码粘贴到你的 smBrain.py 文件中

class MySMClass(sm.SM):
    def getNextValues(self, state, inp):

        return (state, io.Action(fvel=0, rvel=0))





mySM = MySMClass()
mySM.name = 'brainSM'

######################################################################
###
###          Brain methods
###
######################################################################

def plotSonar(sonarNum):
    robot.gfx.addDynamicPlotFunction(y=('sonar'+str(sonarNum),
                                        lambda: 
                                        io.SensorInput().sonars[sonarNum]))

# this function is called when the brain is (re)loaded
def setup():
    robot.gfx = gfx.RobotGraphics(drawSlimeTrail=True, # slime trails
                                  sonarMonitor=True) # sonar monitor widget
    
    # set robot's behavior
    robot.behavior = mySM

# this function is called when the start button is pushed
def brainStart():
    robot.behavior.start(traceTasks = robot.gfx.tasks())

# this function is called 10 times per second
def step():
    # 获取所有传感器输入
    inp = io.SensorInput()

    # 打印每个声纳的距离
    print("--- Sonar Readings ---")
    for i in range(len(inp.sonars)):
        # 使用 .format() 方法来格式化字符串，这与 Python 2.6 兼容
        print("Sonar {0}: {1:.2f} meters".format(i, inp.sonars[i]))
    print("----------------------\n")

    # 驱动机器人行为
    robot.behavior.step(inp).execute()
    io.done(robot.behavior.isDone())
# called when the stop button is pushed
def brainStop():
    pass

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
