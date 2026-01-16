"""
高子轩 2025/10/8
"""
import lib601.sm as sm

class PureFunction(sm.SM):
    """
    Wk3.1.3的结果
    """
    def __init__(self, f):
        self.f = f
    def getNextValues(self,state,inp):
        next_state = state
        output = self.f(inp)
        return next_state, output

def tuple_maxnumber(tup):
    """
    part1要用的返回元组的最大值
    :param tup:
    :return:
    """
    return max(tup)

class BA1(sm.SM):
    startState = 0
    def getNextValues(self, state, inp):
        if inp != 0:
            newState = state * 1.02 + inp - 100
        else:
            newState = state * 1.02
        return (newState, newState)

class BA2(sm.SM):
    startState = 0
    def getNextValues(self, state, inp):
        newState = state * 1.01 + inp
        return (newState, newState)

def choose_account(inp):
    """
    parallel2需要一个二元素的元组作为输入，此函数把inp转换成二元素元组(没有汇入的账户置0)
    :param inp:
    :return:
    """
    if abs(inp) > 3000:
        return (inp,0)
    else:
        return (0,inp)
def plus(tup):
    """
    part2需要用的求和
    :param tup:
    :return:
    """
    return tup[0] + tup[1]
ba1 = BA1()
ba2 = BA2()
get_max = PureFunction(tuple_maxnumber)
maxAccount = sm.Cascade(sm.Parallel(ba1, ba2),get_max)
#输入得到并联状态机的输出，再取最大

get_tuple = PureFunction(choose_account)
get_plus = PureFunction(plus)
switchAccount = sm.Cascade(sm.Cascade(get_tuple,sm.Parallel2(ba1,ba2)),get_plus)
#先把一个inp得到元组，再输入到并联状态机，再作为输入到求和

#下面是测试用例
#inputs = [1000, 0, -500, 5000, 0, -4000]

# def run_test(sm_machine, inputs, name):
#     sm_machine.start()
#     outputs = sm_machine.transduce(inputs)
#
#
#     print "--- {0} 机器测试结果 ---".format(name)
#
#
#     print "输入序列: {0}".format(inputs)
#
#     # 格式化为两位小数
#     formatted_outputs = ["%.2f" % o for o in outputs]
#     print "输出序列: {0}".format(formatted_outputs)
#     print "-" * 30
#     return outputs
#
# # --- 运行测试 ---
# max_outputs = run_test(maxAccount, inputs, "maxAccount (Max Balance)")
# switch_outputs = run_test(switchAccount, inputs, "switchAccount (Total Balance with Routing)")
#
# # --- 预期结果 (供验证) ---
# expected_max =     [1000.00, 1010.00, 520.10, 5525.30, 5580.55, 1636.36]
# expected_switch = [1000.00, 1010.00, 520.10, 5425.30, 5528.55, 1533.82]
#
# print "\n--- 预期结果对比 (仅供参考) ---"
# print "Max Account (预期): {0}".format(["%.2f" % o for o in expected_max])
# print "Switch Account (预期): {0}".format(["%.2f" % o for o in expected_switch])



