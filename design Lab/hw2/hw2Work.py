# -*- coding: cp936 -*-
import lib601.sf as sf
import lib601.sig as sig
import lib601.ts as ts

# 6.01 HomeWork 2 Skeleton File

#Constants relating to some properties of the motor
k_m = 1000
k_b = 0.5
k_s = 5
r_m = 20

#Modeling the sensor and controller
def controllerAndSensorModel(k_c):
    return(sf.Gain(k_s*k_c))

#Modeling the plant
def integrator(T):
    accumulator = sf.FeedbackAdd(sf.R(), sf.Gain(1))
    return sf.Cascade(sf.Gain(T), accumulator)

#Modeling the motor
def motorModel(T):
    alpha = T * k_m / r_m
    beta = T * k_m * k_b / r_m
    H_loop = sf.FeedbackAdd(sf.R(), sf.Gain(1 - beta))
    return sf.Cascade(sf.Gain(alpha), H_loop)

#The combined plant
def plantModel(T):
    return sf.Cascade(motorModel(T),integrator(T))

#the main logic
def lightTrackerModel(T,k_c):
    forward_path = sf.Cascade(controllerAndSensorModel(k_c), plantModel(T))
    return sf.FeedbackSubtract(forward_path,sf.Gain(1))



def plotOutput(sfModel):
    """Plot the output of the given SF, with a unit-step signal as input"""
    smModel = sfModel.differenceEquation().stateMachine()
    outSig = ts.TransducedSignal(sig.StepSignal(), smModel)
    outSig.plot()

T = 0.004


kc3 = 1
model_step123 = lightTrackerModel(T, kc3)
plotOutput(model_step123)

import lib601.sf as sf
import lib601.optimize as optimize
import operator
import math # 用于 sqrt

# ======================================================================
# Step 12 常数定义 (使用 k_m = 1000)
# ======================================================================


# 预先计算的常数
# 注意：在 Python 2 中，确保除法是浮点数除法，我们通过使用浮点常数实现。
K2 = (k_m * k_b) / r_m  # K2 = 25.0
TK2 = T * K2         # TK2 = 0.125
TWO_MINUS_TK2 = 2.0 - TK2 # 2.0 - 0.125 = 1.875
K2_SQUARED = K2 * K2     # K2^2 = 625.0
KM_KS_OVER_RM = (k_m * k_s) / r_m # (1000 * 5) / 20 = 250.0

# ======================================================================
# 目标函数：计算主导极点幅值
# ======================================================================

def dominantPoleMagnitude(kc):
    """
    计算给定 k_c 时系统的主导极点幅值 |z_max|。
    """
    
    # 4 * K1
    FOUR_K1 = 4.0 * KM_KS_OVER_RM * kc
    
    # 判别式 D = K2^2 - 4*K1
    D = K2_SQUARED - FOUR_K1
    
    if D >= 0.0:
        # 极点为实数 (不振荡收敛)
        
        # 极点公式中的根号项: T * sqrt(D)
        # 使用 math.sqrt 确保精度
        radical_term = T * math.sqrt(D)
        
        # 主导极点 (幅值最大的一个): z_max = (TWO_MINUS_TK2 + radical_term) / 2
        z1 = (TWO_MINUS_TK2 + radical_term) / 2.0
        z2 = (TWO_MINUS_TK2 - radical_term) / 2.0
        
        # 返回幅值最大的极点
        return max(abs(z1), abs(z2))
        
    else:
        # 极点为复数 (振荡收敛)。
        # 根据 Step 12 的要求 ('without oscillation')，我们对这个区域施加一个惩罚。
        # 惩罚值使用 1.0，因为临界阻尼的幅值是 0.9375，远小于 1.0。
        return 1.0 

# ======================================================================
# 使用 optimize.optOverLine 搜索最佳 k_c
# ======================================================================

# 搜索范围：
# 理论最佳点是 k_c = 0.625。
# 在 0.0 到略微超过 0.625 的范围内搜索。
kc_min = 0
kc_max = 0.65
num_steps = 1000 

print "正在使用 optOverLine 寻找最佳 k_c..."

# 调用 optOverLine: objective 是 dominantPoleMagnitude，默认寻找最小值。
(bestObjValue, bestKc) = optimize.optOverLine(dominantPoleMagnitude, 
                                             kc_min, 
                                             kc_max, 
                                             num_steps)

print "--- Step 12 优化结果 ---"
print "最佳 Kc (最快不振荡收敛): %.4f" % bestKc
print "最小主导极点幅值: %.4f" % bestObjValue

# 理论结果验证:
# 最佳 Kc 应该约为 0.625
# 最小主导极点幅值应为 0.9375
