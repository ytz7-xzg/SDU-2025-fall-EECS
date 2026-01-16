import lib601.sig as sig
import lib601.ts as ts
import lib601.poly as poly
import lib601.sf as sf
import math

def controller(k):
   return sf.Gain(k)

def plant1(T):
   FeedbackAdd = sf.FeedbackAdd(sf.Gain(1), sf.R())
   return sf.Cascade(sf.Gain(T),sf.Cascade(sf.R(), FeedbackAdd))


def plant2(T, V):
   FeedbackAdd = sf.FeedbackAdd(sf.Gain(1), sf.R())
   return sf.Cascade(sf.Gain(T*V),sf.Cascade(sf.R(), FeedbackAdd))


def wallFollowerModel(k, T, V):
   h_controller = controller(k)
   h_plant1 = plant1(T)
   h_plant2 = plant2(T, V)

   # H_plant_cascade = H_plant1 * H_plant2
   h_plant_cascade = sf.Cascade(h_plant1, h_plant2)

   # H_open = H_controller * H_plant_cascade
   h_open = sf.Cascade(h_controller, h_plant_cascade)
   return sf.FeedbackSubtract(h_open, sf.Gain(1))


def calculate_period(k_value, T_value=0.1, V_value=0.1):
   """
   计算给定 k, T, V 参数下闭环系统的振荡周期（秒）。
   """

   # 1. 构建闭环系统模型
   h_model = wallFollowerModel(k_value, T_value, V_value)

   # 2. 找到主极点 p (dominant pole)
   p = h_model.dominantPole()

   # 检查 p 是否有非零虚部（判断是否振荡）
   if abs(p.imag) < 1e-9:  # 极点是实数，系统不振荡
      return "Not Oscillating"

   # 3. 计算极点的相位角 phi (弧度)
   # 使用 math.atan2(imag, real) 来获取正确的角度
   phi = math.atan2(p.imag, p.real)

   # 4. 计算以样本数计的周期 P
   # P = 2*pi / |phi|
   period_samples = 2 * math.pi / abs(phi)

   # 5. 计算以时间（秒）计的周期 P_time
   period_time = period_samples * T_value

   return period_time


# 示例：运行 Step 10 的计算
T = 0.1
V = 0.1

# 请替换为您在 Checkoff 1 中实际使用的 k 值
k_values_to_test = [25,15,5,2.5]  # 示例 k 值

results = []
for k in k_values_to_test:
   period = calculate_period(k, T, V)
   results.append({'k': k, 'period': period})

# 打印结果 - 适配 Python 2.6.6
print "\n--- Step 10 结果 ---"
print "固定参数: T=%s s, V=%s m/s" % (T, V)
print "k | period (seconds)"
print "--------------------"
for res in results:
   # 使用 % 格式化字符串进行输出
   print "%s | %s" % (res['k'], res['period'])
