"""
高子轩 2025/9/25
"""
import pdb
import lib601.sm as sm
import string
import operator

# 老 tokenize函数
def old_tokenize(inputString):
    """
    把传入字符串切割成词元放在列表返回
    :param inputString: 传入字符串
    :return: 分割后的列表
    """
    seps = ['(', ')', '+', '-', '*', '/', '='] #运算符与括号需要与变量，数字单独分开
    for sep in seps:
        inputString = inputString.replace(sep, ' ' + sep + ' ') #给上述左右加空格，方便split()分割
    return inputString.split()

#用状态机弄的新tokenize函数
class Tokenizer(sm.SM):
    """
    一个状态机，其状态表示为 ("start")。
    'pending_output' 用来解决单步单输出的限制问题。
    """
    startState = ('start', '', None)

    def getNextValues(self, state, inp):
        (mode, token_string, pending_output) = state #state是一个元组，包含三个量(当前模式，处理的字符串，下一个输出)
        seps = ['(', ')', '+', '-', '*', '/', '=']

        # 1. 优先级最高：处理上一步留下的“待办”输出
        # 如果有等待输出的词元，立即输出它，并将状态重置
        if pending_output is not None:
            # 用当前字符 inp 重新从 start 状态开始
            (next_state, _) = self.getNextValues(('start', '', None), inp)
            return (next_state, pending_output)

        # 2. 如果没有待办项，正常处理当前输入字符 inp

        # 情况1: 当前字符是特殊运算符
        if inp in seps:
            if token_string:
                # 如果我们正在收集一个词元 (如 'a')，而现在遇到了 ')'
                # 那么，这一步的输出是 'a'
                output = token_string
                # 下一步的状态将包含“待办”的 ')'
                next_state = ('start', '', inp)
                return (next_state, output)
            else:
                # 如果我们没在收集词元，就直接输出这个分隔符
                return (('start', '', None), inp)

        # 情况2: 当前字符是空格
        elif inp.isspace():
            if token_string:
                # 空格结束了当前词元，输出它
                return (('start', '', None), token_string)
            else:
                # 没在收集词元，就忽略这个空格
                return (('start', '', None), None)

        # 情况3: 当前字符是词元的一部分
        elif mode == 'start': #start是初始状态，通过判断此字符是哪种类型，切换到处理该类型的状态
            if inp.isdigit() or inp == '.':#小数点
                return (('in_number', inp, None), None)
            elif inp.isalpha():
                return (('in_variable', inp, None), None)
            else:
                raise ValueError("Invalid character '" + inp + "'")

        elif mode == 'in_number':
            if inp.isdigit() or inp == '.':#还在数字状态
                return (('in_number', token_string + inp, None), None)
            else: # 防止数字和变量混合在一起
                raise ValueError("Invalid character '" + inp + "' after number")

        elif mode == 'in_variable':
            if inp.isalnum(): # 变量可包含字母和数字
                return (('in_variable', token_string + inp, None), None)
            else:
                raise ValueError("Invalid character '" + inp + "' in variable")

# tokenize 函数 (适配器)
def tokenize(inputString):
    tokenizer_sm = Tokenizer()#实例化一个状态机
    # 在末尾加一个空格，确保最后一个词元被“冲刷”出来
    input_list = list(inputString + ' ')
    # transduce 会运行状态机并返回一个包含所有输出的列表 (包括 None)
    raw_output = tokenizer_sm.transduce(input_list)
    # 过滤掉 None，只留下我们需要的词元
    return [token for token in raw_output if token is not None]

class BinaryOp:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return self.opStr + '(' + \
               str(self.left) + ', ' +\
               str(self.right) + ')'
    __repr__ = __str__

class Sum(BinaryOp):
    opStr = 'Sum'

    def eval(self, env):
        left_val = self.left.eval(env)
        right_val = self.right.eval(env)
        if isNum(left_val) and isNum( right_val):
            return self.left.eval(env) +  right_val #都是数字的话，直接返回计算结果了，加减乘除都是一样的
        else:
            return self.__class__(left_val,  right_val) #__class__()可以方便一些，不用单独写Sum(,)，下面也一样复制过去了
            #这里是惰性(下面的lazy需求)，否则直接相加会报错，下面也同理


class Prod(BinaryOp):
    opStr = 'Prod'

    def eval(self, env):
        left_val = self.left.eval(env)
        right_val = self.right.eval(env)
        if isNum(left_val) and isNum(right_val):
            return self.left.eval(env) * right_val
        else:
            return self.__class__(left_val, right_val)


class Quot(BinaryOp):
    opStr = 'Quot'

    def eval(self, env):
        left_val = self.left.eval(env)
        right_val = self.right.eval(env)
        if isNum(left_val) and isNum(right_val):
            return self.left.eval(env) / right_val
        else:
            return self.__class__(left_val, right_val)


class Diff(BinaryOp):
    opStr = 'Diff'

    def eval(self, env):
        left_val = self.left.eval(env)
        right_val = self.right.eval(env)
        if isNum(left_val) and isNum( right_val):
            return self.left.eval(env) -  right_val
        else:
            return self.__class__(left_val,  right_val)


class Assign(BinaryOp):
    opStr = 'Assign'

    def eval(self, env):
        env[self.left.name] = Number(self.right.eval(env))#给变量赋值，一定把他转换成Number类型
        return None
        
class Number:
    def __init__(self, val):
        self.value = val

    def __str__(self):
        return 'Num(' + str(self.value) + ')'

    __repr__ = __str__ #这样输出都是格式化了，不用担心出现内存地址之类的，下面变量类也同理

    def eval(self, env):
        return self.value #数字就直接返回值就行了


class Variable:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Var(' + self.name + ')'

    __repr__ = __str__

    def eval(self, env):
        if self.name in env:
            return env[self.name] #如果变量已经在env中赋值了，就直接返回取值数字
        else:
            return self #不在数组，返回变量类型，增强lazy
        # return env[self.name] 这个是原先不防lazy的，如果不运行testLazyEval()就不会报错
# characters that are single-character tokens
seps = ['(', ')', '+', '-', '*', '/', '=']

# Convert strings into a list of tokens (strings)


# tokens is a list of tokens
# returns a syntax tree:  an instance of {\tt Number}, {\tt Variable},
# or one of the subclasses of {\tt BinaryOp} 
def parse(tokens):
    """
    传入切割好的列表，利用parseExp()函数递归
    :param tokens: 经过分词好的列表
    :return:
    """
    def parseExp(index):
        token = tokens[index]
        if numberTok(token):
            # 取到的元素是数字类型，单独取数字就会直接弹出了
            # 主要服务于下token == "("，当有表达式的时候 ，(left_tree, op_index) = parseExp(index + 1)，返回的index+1会到操作符op
            return (Number(float(token)), index + 1)

        elif variableTok(token):
            # 取到的元素是变量类型，用途同上
            return (Variable(token), index + 1)

        elif token == '(':
            # 取到元素是左括号，说明是一个赋值语句，一定会有操作符op，左右left_tree,right_tree
            (left_tree, op_index) = parseExp(index + 1) #op_index由数字或变量的分支返回，如果(再出现就再进入一次
            op = tokens[op_index] #获得数字变量返回后的index，右边必然是操作符op
            (right_tree, next_index) = parseExp(op_index + 1) #op 后面就是右边的数字或变量了
            #各种分支，看操作符类型经过__str__返回字符串版本
            if op == '+':
                tree = Sum(left_tree, right_tree)
            elif op == '*':
                tree = Prod(left_tree, right_tree)
            elif op == '-':
                tree = Diff(left_tree, right_tree)
            elif op == '/':
                tree = Quot(left_tree, right_tree)
            elif op == '=':
                tree = Assign(left_tree, right_tree)

            return (tree, next_index + 1) #当双重((的时候，这个是跳出内层(的关键,即完结外层的左分支，

    (parsedExp, next_index) = parseExp(0)
    return parsedExp

# token is a string
# returns True if contains only digits
def numberTok(token):
    for char in token:
        if not char in string.digits: return False
    return True

# token is a string
# returns True its first character is a letter
def variableTok(token):
    for char in token:
        if char in string.letters: return True
    return False

# thing is any Python entity
# returns True if it is a number
def isNum(thing):
    return type(thing) == int or type(thing) == float

# Run calculator interactively
def calc():
    env = {}
    while True:
        e = raw_input('%')            # prints %, returns user input
        print '%', # your expression here
        print '   env =', env

# exprs is a list of strings
# runs calculator on those strings, in sequence, using the same environment
def calcTest(inp):
    """
    集成的计算函数，使用temp接收parse处理后得到的语法树，再使用每个类的eval()函数进行取值
    :param inp: 接收的字符串
    :return: 计算结果，以及存储好的env字典
    """
    env = {}
    for i in inp:
        print("%",i)
        temp = parse(tokenize(i))
        result = temp.eval(env)
        if result:
            print(result)
            print("env =" ,env)
def My_calcTest():
    """
    这是我的初版理解，我以为要获取用户输入，之后再返回env与计算结果
    :return:
    """
    env = {}
    while True:
        inp = input("% ")
        for i in inp:
            temp = parse(tokenize(i))
            result = temp.eval(env)
            if result:
                print(result)
                print("env =", env)

# Simple tokenizer tests
'''Answers are:
['fred']
['777']
['777', 'hi', '33']
['*', '*', '-', ')', '(']
['(', 'hi', '*', 'ho', ')']
['(', 'fred', '+', 'george', ')']
['(', 'hi', '*', 'ho', ')']
['(', 'fred', '+', 'george', ')']
'''
def testTokenize():
    print tokenize('fred ')
    print tokenize('777 ')
    print tokenize('777 hi 33 ')
    print tokenize('**-)(')
    print tokenize('( hi * ho )')
    print tokenize('(fred + george)')
    print tokenize('(hi*ho)')
    print tokenize('( fred+george )')


# Simple parsing tests from the handout
'''Answers are:
Var(a)
Num(888.0)
Sum(Var(fred), Var(george))
Quot(Prod(Var(a), Var(b)), Diff(Var(cee), Var(doh)))
Quot(Prod(Var(a), Var(b)), Diff(Var(cee), Var(doh)))
Assign(Var(a), Prod(Num(3.0), Num(5.0)))
'''
def testParse():
    print parse(['a'])
    print parse(['888'])
    print parse(['(', 'fred', '+', 'george', ')'])
    print parse(['(', '(', 'a', '*', 'b', ')', '/', '(', 'cee', '-', 'doh', ')' ,')'])
    print parse(tokenize('((a * b) / (cee - doh))'))
    print parse(tokenize('(a = (3 * 5))'))

####################################################################
# Test cases for EAGER evaluator
####################################################################

def testEval():
    env = {}
    Assign(Variable('a'), Number(5.0)).eval(env)
    print Variable('a').eval(env)
    env['b'] = 2.0
    print Variable('b').eval(env)
    env['c'] = 4.0
    print Variable('c').eval(env)
    print Sum(Variable('a'), Variable('b')).eval(env)
    print Sum(Diff(Variable('a'), Variable('c')), Variable('b')).eval(env)
    Assign(Variable('a'), Sum(Variable('a'), Variable('b'))).eval(env)
    print Variable('a').eval(env)
    print env

# Basic calculator test cases (see handout)
testExprs = ['(2 + 5)',
             '(z = 6)',
             'z',
             '(w = (z + 1))',
             'w'
             ]
# calcTest(testExprs)

####################################################################
# Test cases for LAZY evaluator
####################################################################

# Simple lazy eval test cases from handout
'''Answers are:
Sum(Var(b), Var(c))
Sum(2.0, Var(c))
6.0
'''
def testLazyEval():
    env = {}
    Assign(Variable('a'), Sum(Variable('b'), Variable('c'))).eval(env)
    print Variable('a').eval(env)
    env['b'] = Number(2.0)
    print Variable('a').eval(env)
    env['c'] = Number(4.0)
    print Variable('a').eval(env)

# Lazy partial eval test cases (see handout)
lazyTestExprs = ['(a = (b + c))',
                  '(b = ((d * e) / 2))',
                  'a',
                  '(d = 6)',
                  '(e = 5)',
                  'a',
                  '(c = 9)',
                  'a',
                  '(d = 2)',
                  'a']
# calcTest(lazyTestExprs)

## More test cases (see handout)
partialTestExprs = ['(z = (y + w))',
                    'z',
                    '(y = 2)',
                    'z',
                    '(w = 4)',
                    'z',
                    '(w = 100)',
                    'z']

def TestTokenize(): #这是6.1中的测试用例，我粘贴到这里来了
    Tokenizer().transduce('fred ')
    Tokenizer().transduce('777 ')
    Tokenizer().transduce(' ** -)(')
    Tokenizer().transduce('(hi * ho) ')
    Tokenizer().transduce('(fred + george) ')
# calcTest(partialTestExprs)
testTokenize()
testParse()
testEval()
calcTest(testExprs)
testLazyEval()
calcTest(lazyTestExprs)
TestTokenize()

