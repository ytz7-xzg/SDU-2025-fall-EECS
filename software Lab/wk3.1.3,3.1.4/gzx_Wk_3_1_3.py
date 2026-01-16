class PureFunction(sm.SM):
    def __init__(self, f):
        self.f = f
    def getNextValues(self,state,inp):
        next_state = state
        output = self.f(inp)
        return next_state, output