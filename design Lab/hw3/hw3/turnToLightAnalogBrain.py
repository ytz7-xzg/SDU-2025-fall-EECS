import math
import lib601.util as util
import lib601.sm as sm
import lib601.gfx as gfx
from soar.io import io

class MySMClass(sm.SM):
    def __init__(self, gain=1.0, threshold=0.1):
        self.startState = 'searching'
        self.gain = gain  # 控制增益，可调节
        self.threshold = threshold  # 光强差异阈值
        # 光电传感器偏置校正（解决不匹配问题）
        self.left_bias = 0.0
        self.right_bias = 0.0
        
    def getNextValues(self, state, inp):
        # 读取传感器数据
        # 通道0: 颈部电位器（用于绘图和稳定时间计算）
        # 通道1: 左光电传感器
        # 通道2: 右光电传感器
        try:
            left_light = inp.analogInputs[1] + self.left_bias
            right_light = inp.analogInputs[2] + self.right_bias
        except IndexError:
            # 如果通道号不对，使用默认值
            left_light = 1.0
            right_light = 1.0
        
        # 计算光强差异（归一化处理）
        light_sum = left_light + right_light
        if light_sum > 0:
            # 归一化差异，范围大约在[-1, 1]
            diff = (left_light - right_light) / light_sum
        else:
            diff = 0
        
        # 控制逻辑：比例控制
        if abs(diff) < self.threshold:
            # 光线均衡，停止转动
            rvel = 0.0
            nextState = 'locked'
        else:
            # 比例控制：差异越大，转动速度越快
            rvel = -self.gain * diff  # 负号是因为左右方向定义
            # 限制最大角速度，避免剧烈运动
            if rvel > 1.0:
                rvel = 1.0
            elif rvel < -1.0:
                rvel = -1.0
            nextState = 'turning'
        
        return (nextState, io.Action(fvel=0.0, rvel=rvel))
    
    def setGain(self, new_gain):
        """设置控制增益，用于步骤5的性能测试"""
        self.gain = new_gain
    
    def setBias(self, left_bias=0.0, right_bias=0.0):
        """设置传感器偏置，用于步骤7的精度优化"""
        self.left_bias = left_bias
        self.right_bias = right_bias

# 创建状态机实例，可调节参数
mySM = MySMClass(gain=1.0, threshold=0.05)
mySM.name = 'lightTrackingSM'

def settleTime(samples):
    """计算稳定时间：系统从开始运动到稳定所需时间步数"""
    if len(samples) < 10:
        return 0
    
    # 计算5%的误差范围
    sample_max = max(samples)
    sample_min = min(samples)
    epsilon = (sample_max - sample_min) * 0.05
    if epsilon < 0.001:  # 防止除零和过小值
        epsilon = 0.001
    
    # 找到开始运动的时刻（首次偏离初始值超过epsilon）
    lastUnchangedIdx = None
    for i in range(len(samples)):
        if abs(samples[i] - samples[0]) >= epsilon:
            lastUnchangedIdx = i - 1
            break
    
    # 找到稳定时刻（最后偏离最终值超过epsilon）
    lastBadIdx = None
    for i in range(len(samples) - 1, -1, -1):
        if abs(samples[i] - samples[-1]) > epsilon:
            lastBadIdx = i
            break
    
    if lastUnchangedIdx is not None and lastBadIdx is not None:
        settle_time = lastBadIdx - lastUnchangedIdx + 1
        if settle_time < 0:
            settle_time = 0
        return settle_time
    else:
        return 0

######################################################################
###
###          Brain methods
###
######################################################################

def setup():
    """初始化图形界面"""
    robot.gfx = gfx.RobotGraphics(drawSlimeTrail=False)
    
    # 静态绘图：颈部电位器电压 vs 时间
    robot.gfx.addStaticPlotFunction(
        y=('neck potentiometer (V)', lambda inp: inp.analogInputs[0]))
    
    print "Light tracking system initialized"
    try:
        sensor_input = io.SensorInput()
        print "Available analog inputs:", len(sensor_input.analogInputs)
    except:
        print "Cannot read sensor inputs"

def brainStart():
    """脑部启动函数"""
    robot.behavior = mySM
    robot.behavior.start(robot.gfx.tasks())
    robot.data = []  # 存储颈部电位器数据
    robot.step_count = 0
    
    print "Brain started - Light tracking activated"
    print "Current gain:", mySM.gain

def step():
    """每一步执行的控制逻辑"""
    inp = io.SensorInput()
    
    # 执行控制行为
    robot.behavior.step(inp).execute()
    
    # 记录数据用于稳定时间计算
    neck = inp.analogInputs[0]
    robot.data.append(neck)
    robot.step_count = robot.step_count + 1
    
    # 可选：实时显示传感器读数（用于调试）
    if robot.step_count % 20 == 0:  # 每20步显示一次
        if len(inp.analogInputs) > 2:
            print "Step " + str(robot.step_count) + ": Neck=%.3fV, Lights=(%.3f, %.3f)" % (
                neck, inp.analogInputs[1], inp.analogInputs[2])

def brainStop():
    """脑部停止函数"""
    if hasattr(robot, 'data') and robot.data:
        stime = settleTime(robot.data)
        print 'Settle time: ' + str(stime) + ' steps'
        
        # 显示数据统计
        print 'Total steps: ' + str(len(robot.data))
        print 'Neck pot range: %.3fV to %.3fV' % (min(robot.data), max(robot.data))
        
        # 保存数据用于分析（可选）
        try:
            f = open('light_tracking_data.txt', 'w')
            for i in range(len(robot.data)):
                f.write(str(i) + "\t" + str(robot.data[i]) + "\n")
            f.close()
            print "Data saved to light_tracking_data.txt"
        except:
            print "Could not save data file"
    else:
        print 'No data collected'

def shutdown():
    """关闭函数"""
    print "Light tracking system shutdown"

# 实验辅助函数
def testDifferentGains(gains_to_test):
    """测试不同增益的性能（用于步骤5）"""
    print "\n=== Testing different gains ==="
    results = {}
    
    for gain in gains_to_test:
        print "\nTesting gain = " + str(gain)
        mySM.setGain(gain)
        # 这里需要实际运行测试并记录结果
        results[gain] = {"settle_time": 0, "performance": "待测试"}
    
    return results

def calibrateSensors():
    """校准光电传感器（用于步骤7的精度优化）"""
    print "\n=== Calibrating light sensors ==="
    # 在实际均匀光照下测量传感器读数，计算偏置
    # 这需要在实验环境中手动执行
    print "Place robot in uniform light and run calibration"
    return {"left_bias": 0.0, "right_bias": 0.0}

# 兼容性修复：确保所有函数都存在
try:
    # 检查必要的函数是否存在
    if not hasattr(robot, 'gfx'):
        robot.gfx = None
    if not hasattr(robot, 'behavior'):
        robot.behavior = None
    if not hasattr(robot, 'data'):
        robot.data = []
except:
    pass
