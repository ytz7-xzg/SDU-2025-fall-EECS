# -*- coding: utf-8 -*-
import lib601.util as util
import lib601.dist as dist
import lib601.distPlot as distPlot
import lib601.sm as sm
import lib601.ssm as ssm
import lib601.sonarDist as sonarDist
import lib601.move as move
import lib601.seGraphics as seGraphics
import lib601.idealReadings as idealReadings

# For testing your preprocessor
class SensorInput:
    def __init__(self, sonars, odometry):
        self.sonars = sonars
        self.odometry = odometry

preProcessTestData = [SensorInput([0.8, 1.0], util.Pose(1.0, 0.5, 0.0)),
                       SensorInput([0.25, 1.2], util.Pose(2.4, 0.5, 0.0)),
                       SensorInput([0.16, 0.2], util.Pose(7.3, 0.5, 0.0))]
testIdealReadings = ( 5, 1, 1, 5, 1, 1, 1, 5, 1, 5 )
testIdealReadings100 = ( 50, 10, 10, 50, 10, 10, 10, 50, 10, 50 )


class PreProcess(sm.SM):
    
    def __init__(self, numObservations, stateWidth):
        self.startState = (None, None)
        self.numObservations = numObservations
        self.stateWidth = stateWidth

    def getNextValues(self, state, inp):
        (lastUpdatePose, lastUpdateSonar) = state
        currentPose = inp.odometry
        currentSonar = idealReadings.discreteSonar(inp.sonars[0],
                                                   self.numObservations)
        # Handle the first step
        if lastUpdatePose == None:
            return ((currentPose, currentSonar), None)
        else:
            action = discreteAction(lastUpdatePose, currentPose,
                                    self.stateWidth)
            print (lastUpdateSonar, action)
            return ((currentPose, currentSonar), (lastUpdateSonar, action))

# Only works when headed to the right
def discreteAction(oldPose, newPose, stateWidth):
    return int(round(oldPose.distance(newPose) / stateWidth))

def makeRobotNavModel(ideal, xMin, xMax, numStates, numObservations):
    startDistribution = dist.squareDist(0, numStates)# redefine this
    #开始的时候保持概率的均匀分布作为初始分布
    def observationModel(ix):
        idealObservation = ideal[ix]

        # 1. 准读数 (Triangle): 宽度设为 4
        triangle_dist = dist.triangleDist(idealObservation, 4)

        # 2. 瞎读数 (Uniform): 全范围均匀
        uniform_dist = dist.squareDist(0, numObservations)

        # 3. 坏读数 (Max Range Spike): 集中在最大值
        max_dist = dist.DeltaDist(numObservations - 1)

        # 4. 混合 (Mixture):
        # 因为 MixtureDist 只能混合两个，所以我们需要分两步走

        # 第一步: 混合 Uniform(0.4) 和 Max(0.1)
        # 它们的总概率是 0.5，其中 Uniform 占 0.4/0.5 = 0.8
        tail_dist = dist.MixtureDist(uniform_dist, max_dist, 0.8)

        # 第二步: 混合 Triangle(0.5) 和 上面的 tail_dist(0.5)
        # 概率 p=0.5 给 Triangle，剩下的给 tail_dist
        combined_dist = dist.MixtureDist(triangle_dist, tail_dist, 0.9)

        return combined_dist
        # ix is a discrete location of the robot
        # return a distribution over observations in that state

    def transitionModel(a):
        def transition(oldPos):
            # 1. 计算理想位置
            # 增加 "撞墙逻辑"：如果超出边界 (numStates-1)，就取边界值
            # 同时也防止走出左边边界 (max(..., 0))
            idealPos = oldPos + a

            # 限制 idealPos 必须在合法索引 [0, numStates-1] 之间
            if idealPos > numStates - 1:
                idealPos = numStates - 1
            elif idealPos < 0:
                idealPos = 0

            width = 1
            # 2. 返回分布
            return dist.triangleDist(idealPos, width, 0, numStates)

        return transition

    return ssm.StochasticSM(startDistribution, transitionModel,
                            observationModel)

# Main procedure
def makeLineLocalizer(numObservations, numStates, ideal, xMin, xMax, robotY):
    # 1. 计算状态宽度 (stateWidth)
    # 用于 Preprocessor 将连续距离转换为离散动作步数
    stateWidth = (xMax - xMin) / float(numStates)

    # 2. 创建 预处理器 (Preprocessor)
    # [cite: 43] 类名为 PreProcess
    preproc = PreProcess(numObservations, stateWidth)

    # 3. 创建 导航模型 (SSM)
    # 使用我们在 Step 3-6 中实现的函数
    navModel = makeRobotNavModel(ideal, xMin, xMax, numStates, numObservations)

    # 4. 创建 状态估计器 (Estimator)
    # [cite: 78, 189] 使用 seGraphics.StateEstimator 来获得图形化显示
    estimator = seGraphics.StateEstimator(navModel)

    # 5. 创建 驱动器 (Driver)
    # [cite: 211] 这是一个移动到固定位置的状态机
    # 目标是 (xMax, robotY)，速度 0.5
    driver = move.MoveToFixedPose(util.Pose(xMax, robotY, 0.0), maxVel=0.5)

    # 6. 组装系统 (Putting it All Together)
    # [cite: 206-207]

    # 路径 A: 估算 (PreProcess -> Estimator)
    # 输入: SensorInput -> 输出: Belief (显示在窗口中)
    est_path = sm.Cascade(preproc, estimator)

    # 路径 B: 驱动 (Driver)
    # 输入: SensorInput -> 输出: Action

    # 并行组合: 同时运行估算和驱动
    # 输入: SensorInput -> 输出: (Belief, Action)
    combined = sm.Parallel(est_path, driver)

    # 选择输出: 我们只需要 Action 来控制机器人
    # select(1) 取元组的第 2 个元素 (索引1)
    # 输入: (Belief, Action) -> 输出: Action
    return sm.Cascade(combined, sm.Select(1))

# # 1. 实例化模型 (使用测试数据)
# model100 = makeRobotNavModel(testIdealReadings100, 0.0, 10.0, 10, 100)
# # 2. 获取在位置 7 的观测概率分布
# # 位置 7 的理想读数是 5 (参见 testIdealReadings)
# obs_dist = model100.observationDistribution(7)
# # 3. 打印概率最高的 4 个观测值 [cite: 188]
# # 你应该看到观测值 5 的概率最高，周围递减，且 9 (Max) 也有一定概率
# print(obs_dist)
# # 或者绘图
# distPlot.plot(obs_dist)
# if __name__ == '__main__':
#     # 1. 创建模型
#     # 使用测试用的理想读数
#     model = makeRobotNavModel(testIdealReadings, 0.0, 10.0, 10, 10)
#
#     # 2. 获取转移模型
#     # transitionModel 是模型里的一个属性
#     trans_model = model.transitionDistribution
#
#     # 3. 测试 Step 6 的要求：Action=2, OldPos=5
#     # 语法解释：先调用 trans_model(2) 拿到特定动作的函数
#     #          再调用 (5) 拿到从位置5出发的分布
#     next_pos_dist = trans_model(2)(5)
#
#     print(next_pos_dist)
#     distPlot.plot(next_pos_dist)
if __name__ == '__main__':
    # 1. 定义参数
    numStates = 10
    numObservations = 10
    xMin = 0.0
    xMax = 10.0
    stateWidth = (xMax - xMin) / numStates

    # 2. 创建你的数学模型 (Initial + Obs + Trans)
    # 使用 Step 3, 4, 6 写好的函数
    model = makeRobotNavModel(testIdealReadings, xMin, xMax, numStates, numObservations)

    # 3. 创建两个核心机器
    # A. 预处理器
    preprocessor = PreProcess(numObservations, stateWidth)
    # B. 估计器 (注意这里用 seGraphics.StateEstimator)
    estimator = seGraphics.StateEstimator(model)

    # 4. 级联 (连接水管)
    # preprocessor 的输出会自动喂给 estimator 的输入
    ppEst = sm.Cascade(preprocessor, estimator)

    # 5. 运行测试数据
    # transduce 会返回每一步的最终输出(信念分布)
    belief_sequence = ppEst.transduce(preProcessTestData)

    # 6. 打印最后几步的信念，看看机器人是否定位成功
    # 打印最后一步的信念分布
    print(belief_sequence[-1])