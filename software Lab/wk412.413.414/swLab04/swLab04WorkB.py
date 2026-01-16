import lib601.poly as poly
import swLab04SignalDefinitions
reload(swLab04SignalDefinitions) # so changes you make in swLab04SignalDefinitions.py will be reloaded
from swLab04SignalDefinitions import *

# =================================================================
# 以下是 Step 3 的示例测试代码
# 将此代码块粘贴到 swLab04WorkB.py 文件中以测试您的实现
# =================================================================

# 文件 swLab04WorkB.py 会自动导入你在 swLab04SignalDefinitions.py 中定义的类

# 1. 创建一个基础信号实例用于测试
# 我们将使用你自己实现的 StepSignal
try:
    s = StepSignal()
    print("成功创建 StepSignal 实例。")
except NameError:
    print("错误: StepSignal 类似乎未在 swLab04SignalDefinitions.py 中定义。")
    # 如果基类未定义，则退出，因为后续测试依赖于它
    exit()


# 2. 测试 StepSignal
# 绘制信号 s 从 n=-5 到 n=5 的图像。
# 预期结果：在 n=0 处，信号从 0 跳变到 1
print("\n正在绘制 StepSignal...")
s.plot(start=-5, end=5, newWindow='测试: StepSignal')


# 3. 测试 ScaledSignal
# 将阶跃信号 s 乘以常数 2.5
# 预期结果：信号在 n=0 处从 0 跳变到 2.5
print("正在绘制 ScaledSignal(s, 2.5)...")
scaled_s = ScaledSignal(s, 2.5)
scaled_s.plot(start=-5, end=5, newWindow='测试: ScaledSignal')


# 4. 测试 R (延迟一个时间步)
# 将阶跃信号 s 延迟 1 个单位
# 预期结果：信号的跳变点从 n=0 移动到 n=1
print("正在绘制 R(s)...")
delayed_s1 = R(s)
delayed_s1.plot(start=-5, end=5, newWindow='测试: R (延迟1步)')


# 5. 测试 Rn (延迟 k 个时间步)
# 将阶跃信号 s 延迟 3 个单位
# 预期结果：信号的跳变点从 n=0 移动到 n=3
print("正在绘制 Rn(s, 3)...")
delayed_s3 = Rn(s, 3)
delayed_s3.plot(start=-5, end=5, newWindow='测试: Rn (延迟3步)')


# 6. 测试 SummedSignal
# 将原始阶跃信号 s 与延迟了3步的信号 delayed_s3 相加
# 预期结果：
#   - 在 n < 0 时, 值为 0 + 0 = 0
#   - 在 0 <= n < 3 时, 值为 1 + 0 = 1
#   - 在 n >= 3 时, 值为 1 + 1 = 2
print("正在绘制 SummedSignal(s, delayed_s3)...")
summed_s = SummedSignal(s, delayed_s3)
summed_s.plot(start=-5, end=5, newWindow='测试: SummedSignal')

print("\n测试代码执行完毕。请检查弹出的绘图窗口。")