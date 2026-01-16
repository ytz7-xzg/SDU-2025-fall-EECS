# -*- coding: utf-8 -*-
import math
import lib601.sonarDist as sonarDist
import lib601.sm as sm
import lib601.util as util
import lib601.gridMap as gridMap
import lib601.dynamicGridMap as dynamicGridMap
import lib601.dynamicCountingGridMap as dynamicCountingGridMap
import bayesMapSkeleton as bayesMap
reload(bayesMap)

class MapMaker(sm.SM):
    def __init__(self, xMin, xMax, yMin, yMax, gridSquareSize):
        # 初始化状态：创建一个空的 DynamicGridMap 实例 [cite: 60, 71]
        self.startState = bayesMap.BayesGridMap(xMin, xMax, yMin, yMax, gridSquareSize)

    def getNextValues(self, state, inp):
        # 1. 获取机器人的位置作为射线起点reading
        robotPose = inp.odometry
        startPoint = util.Point(robotPose.x, robotPose.y)
        startIndices = state.pointToIndices(startPoint)

        # 遍历每一个声纳传感器的读数
        for i in range(len(inp.sonars)):
            reading = inp.sonars[i]
            if reading < 0.1:
                continue
            sonarPose = sonarDist.sonarPoses[i]

            # 2. 确定射线的有效长度
            dist = reading
            if dist > sonarDist.sonarMax:
                dist = sonarDist.sonarMax

            # 3. 计算射线终点
            # 注意：这里直接调用 lib601 提供的 sonarDist.sonarHit
            hitPoint = sonarDist.sonarHit(dist, sonarPose, robotPose)
            endIndices = state.pointToIndices(hitPoint)

            # 边界检查
            if startIndices is None or endIndices is None:
                continue

            # 4. 获取射线路径上的所有格子
            cellIndices = util.lineIndices(startIndices, endIndices)

            # 5. 根据读数更新地图 (修正了这里！)
            if reading < sonarDist.sonarMax:
                # --- 情况 A: 真的打到了障碍物 ---

                # 路径上的点（除了最后一个）用 clearCell 涂白
                for cell in cellIndices[:-1]:
                    state.clearCell(cell)

                # 最后一个点用 setCell 涂黑 (不需要传 1)
                state.setCell(cellIndices[-1])

            else:
                # # --- 情况 B: 前方无障碍 ---
                #
                # # 整条路径都用 clearCell 涂白
                for cell in cellIndices:
                    state.clearCell(cell)

        # 返回修改后的 state 对象
        return (state, state)
                
# For testing your map maker
class SensorInput:
    def __init__(self, sonars, odometry):
        self.sonars = sonars
        self.odometry = odometry

testData = [SensorInput([0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
                        util.Pose(1.0, 2.0, 0.0)),
            SensorInput([0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4],
                        util.Pose(4.0, 2.0, -math.pi))]

testClearData = [SensorInput([1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, 1.0],
                             util.Pose(1.0, 2.0, 0.0)),
                 SensorInput([1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, 1.0],
                             util.Pose(4.0, 2.0, -math.pi))]

def testMapMaker(data):
    (xMin, xMax, yMin, yMax, gridSquareSize) = (0, 5, 0, 5, 0.1)
    mapper = MapMaker(xMin, xMax, yMin, yMax, gridSquareSize)
    mapper.transduce(data)
    mapper.startState.drawWorld()

def testMapMakerClear(data):
    (xMin, xMax, yMin, yMax, gridSquareSize) = (0, 5, 0, 5, 0.1)
    mapper = MapMaker(xMin, xMax, yMin, yMax, gridSquareSize)
    for i in range(50):
        for j in range(50):
            mapper.startState.setCell((i, j))
    mapper.transduce(data)
    mapper.startState.drawWorld()

def testMapMakerN(n, data):
    (xMin, xMax, yMin, yMax, gridSquareSize) = (0, 5, 0, 5, 0.1)
    mapper = MapMaker(xMin, xMax, yMin, yMax, gridSquareSize)
    mapper.transduce(data*n)
    mapper.startState.drawWorld()

testClearData = [SensorInput([1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, 1.0],
                             util.Pose(1.0, 2.0, 0.0)),
                 SensorInput([1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, 1.0],
                             util.Pose(4.0, 2.0, -math.pi))]

