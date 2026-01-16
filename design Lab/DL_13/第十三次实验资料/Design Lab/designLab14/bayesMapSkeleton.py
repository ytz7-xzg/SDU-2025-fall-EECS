# -*- coding: utf-8 -*-
import lib601.dist as dist
import lib601.util as util
import lib601.colors as colors
import lib601.ssm as ssm
import lib601.seFast as seFast
import lib601.dynamicGridMap as dynamicGridMap


# Define the stochastic state-machine model for a given cell here.

# Observation model:  P(obs | state)
def oGivenS(s):
    if s == True:
        # 如果是墙，90% 概率看到 'hit'，10% 概率看到 'free' (噪声)
        return dist.DDist({'hit': 0.9, 'free': 0.1})
    else:
        # 如果是空，90% 概率看到 'free'，10% 概率看到 'hit' (噪声)
        return dist.DDist({'hit': 0.1, 'free': 0.9})
# Transition model: P(newState | s | a)
def uGivenAS(a):
     return lambda s: dist.DDist({s: 1.0})
cellSSM = ssm.StochasticSM(dist.DDist({True: 0.5, False: 0.5}),
                           uGivenAS, oGivenS)

class BayesGridMap(dynamicGridMap.DynamicGridMap):

    def squareColor(self, (xIndex, yIndex)):
        p = self.occProb((xIndex, yIndex))
        if self.robotCanOccupy((xIndex,yIndex)):
            return colors.probToMapColor(p, colors.greenHue)
        elif self.occupied((xIndex, yIndex)):
            return 'black'
        else:
            return 'red'
        
    def occProb(self, (xIndex, yIndex)):
        return self.grid[xIndex][yIndex].state.prob(True)
    def makeStartingGrid(self):
        grid = util.make2DArrayFill(self.xN, self.yN,
                                    lambda x, y: seFast.StateEstimator(cellSSM))

        # [关键点 2] 极其重要！必须启动每一个状态机，否则它们没有初始状态
        # 引用自 Lab Step 11
        for x in range(self.xN):
            for y in range(self.yN):
                grid[x][y].start()

        return grid
    def setCell(self, (xIndex, yIndex)):
        self.grid[xIndex][yIndex].step(('hit', None))
        self.drawSquare((xIndex, yIndex))  # 重绘该格子
    def clearCell(self, (xIndex, yIndex)):
        self.grid[xIndex][yIndex].step(('free', None))
        self.drawSquare((xIndex, yIndex))  # 重绘该格子
    def occupied(self, (xIndex, yIndex)):
        return self.occProb((xIndex, yIndex)) > 0.7

mostlyHits = [('hit', None), ('hit', None), ('hit', None), ('free', None)]
mostlyFree = [('free', None), ('free', None), ('free', None), ('hit', None)]

def testCellDynamics(cellSSM, input):
    se = seFast.StateEstimator(cellSSM)
    return se.transduce(input)

