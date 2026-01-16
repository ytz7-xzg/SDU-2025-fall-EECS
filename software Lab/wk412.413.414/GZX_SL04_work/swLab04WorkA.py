import lib601.poly as poly
import lib601.sig
from lib601.sig import *

## You can evaluate expressions that use any of the classes or
## functions from the sig module (Signals class, etc.).  You do not
## need to prefix them with "sig."


class StepSignal(Signal):
    def sample(self,n):
        if n < 0:
            return 0
        else:
            return 1
class SummedSignal(Signal):
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2
    def sample(self, n):
        return self.s1.sample(n)+self.s2.sample(n)

class ScaledSignal(Signal):
    def __init__(self, s, c):
        self.s = s
        self.c = c
    def sample(self, n):
        return self.c * self.s.sample(n)

def R(Signal):
    def __init__(self, s):
        self.s = s

    def sample(self, n):
        return self.s.sample(n - 1)

class Rn(Signal):
    def __init__(self, s, k):
        self.s = s
        self.k = k

    def sample(self, n):
        return self.s.sample(n - self.k)