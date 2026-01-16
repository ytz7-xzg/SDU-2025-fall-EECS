import math
import lib601.util as util
import lib601.sm as sm
import lib601.gfx as gfx
from soar.io import io

# 将这部分代码粘贴到你的 smBrain.py 文件中

class MySMClass(sm.SM):
    def getNextValues(self, state, inp):
        # 目标距离是 0.5 米
        target_distance = 0.5

        # 获取前方声纳传感器（声纳 3）的读数
        # 假设 inp.sonars 是一个包含8个声纳读数的列表 [cite: 68]S
        # 声纳 3 是其中一个前向传感器
        front_distance = inp.sonars[3]

        # 计算误差
        error = front_distance - target_distance

        # 根据误差调整速度，使用简单的比例控制
        # 比例系数可以根据实际情况进行调整，这里我们用一个经验值
        # 负号是因为如果距离太远（正误差），我们需要加速前进
        # 如果距离太近（负误差），我们需要减速或后退
        fvel = error * 0.1 # 这里的 0.5 是一个比例增益，你可以根据需要调整

        # 确保速度在规定的范围内 (-0.3 到 0.3)
        # 文档要求前进速度不超过 0.3 [cite: 94]
        if fvel > 0.3:
            fvel = 0.3
        elif fvel < -0.3:
            fvel = -0.3

        # 不进行转弯，所以角速度为 0
        rvel = 0.0

        # 返回下一个状态和行动
        # 在这个简单的任务中，状态保持不变
        return (state, io.Action(fvel=fvel, rvel=rvel))





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
