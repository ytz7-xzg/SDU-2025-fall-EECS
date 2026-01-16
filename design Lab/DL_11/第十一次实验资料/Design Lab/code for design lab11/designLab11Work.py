import lib601.dist as dist
import lib601.coloredHall as coloredHall
from lib601.coloredHall import *

standardHallway = ['white', 'white', 'green', 'white', 'white']
alternating = ['white', 'green'] * 6
sterile = ['white'] * 16
testHallway = ['chocolate', 'white', 'green', 'white', 'white',
               'green', 'green', 'white',  
               'green', 'white', 'green', 'chocolate']

maxAction = 5
actions = [str(x) for x in range(maxAction) + [-x for x in range(1, maxAction)]]

def makePerfect(hallway = standardHallway):
    return makeSim(hallway, actions, perfectObsNoiseModel,
                   standardDynamics, perfectTransNoiseModel,'perfect')

def makeNoisy(hallway = standardHallway):
    return  makeSim(hallway, actions, noisyObsNoiseModel, standardDynamics,
                    noisyTransNoiseModel, 'noisy')

def makeNoisyKnownInitLoc(initLoc, hallway = standardHallway):
    return  makeSim(hallway, actions, noisyObsNoiseModel, standardDynamics,
                    noisyTransNoiseModel, 'known init',
                    initialDist = dist.DDist({initLoc: 1}))

def whiteEqGreenObsDist(actualColor):
    # 如果真实颜色是白色或绿色
    if actualColor == 'white' or actualColor == 'green':
        # 看到白色的概率是0.5，看到绿色的概率是0.5
        return dist.DDist({'white': 0.5, 'green': 0.5})
    else:
        # 其他颜色完美观测（概率为1.0）
        return dist.DDist({actualColor: 1.0})

def whiteVsGreenObsDist(actualColor):
    if actualColor == 'white':
        # 真实是白色，总是看到绿色
        return dist.DDist({'green': 1.0})
    elif actualColor == 'green':
        # 真实是绿色，总是看到白色
        return dist.DDist({'white': 1.0})
    else:
        # 其他颜色完美观测
        return dist.DDist({actualColor: 1.0})




