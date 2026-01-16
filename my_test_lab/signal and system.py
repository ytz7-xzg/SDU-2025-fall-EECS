# -*- coding: utf-8 -*-
#
# Adapted for Python 2.6.6 compatibility.
# Key changes: `print` is a statement, not a function, 
# and f-string formatting is replaced with older style.
#

import lib601.sm as sm
# Note: In a real environment, you might need a utility for safeAdd,
# but for this example, we assume standard addition.
# from lib601.util import safeAdd 

class Increment(sm.SM):
    """
    A stateless machine whose output is the input incremented by a given value.
    This version uses getNextState, relying on the default getNextValues
    from the SM class to make the output the same as the next state.
    [cite_start][cite: 661-666]
    """
    def __init__(self, incr):
        self.incr = incr

    def getNextState(self, state, inp):
        # In a real implementation, this would use safeAdd.
        return inp + self.incr

class Delay(sm.SM):
    """
    A machine that delays its input stream by one time step.
    The initial output is specified at initialization.
    [cite_start][cite: 429-433]
    """
    def __init__(self, v0):
        self.startState = v0
        
    def getNextValues(self, state, inp):
        # Returns (next state, current output)
        return (inp, state)

class Cascade(sm.SM):
    """
    A machine that represents the cascade composition of two state machines.
    The output of the first machine is the input to the second.
    (Note: The full implementation is in the sm library, this is a conceptual representation)
    """
    def __init__(self, m1, m2):
        self.m1 = m1
        self.m2 = m2
        self.startState = (self.m1.startState, self.m2.startState)

    def getNextValues(self, state, inp):
        (s1, s2) = state
        (new_s1, o1) = self.m1.getNextValues(s1, inp)
        (new_s2, o2) = self.m2.getNextValues(s2, o1) # o1 is the input to m2
        return ((new_s1, new_s2), o2)

class Feedback(sm.SM):
    """
    Represents the feedback composition of a state machine.
    The output of the machine is fed back into its own input.
    The machine must have a delay between input and output.
    [cite_start][cite: 813-816, 830-831]
    """
    def __init__(self, m):
        self.m = m
        self.startState = self.m.startState
    
    def getNextValues(self, state, inp):
        # First, get the output by passing 'undefined' as the input.
        # This works if the output depends only on the state.
        (ignore, o) = self.m.getNextValues(state, 'undefined')
        
        # Then, get the next state by passing the actual output `o`
        # as the feedback input.
        (newS, ignore) = self.m.getNextValues(state, o)
        
        # The final result is the new state and the calculated output.
        return (newS, o)

def makeCounter(init, step):
    """
    Creates a counter machine that starts at `init` and increments by `step`.
    It is a feedback composition of a cascade of an Increment and a Delay machine.
    [cite_start][cite: 834-835]
    """
    # The structure is Feedback( Cascade( Increment, Delay ) )
    internal_machine = Cascade(Increment(step), Delay(init))
    return Feedback(internal_machine)

# --- Example Usage (Python 2.6.6 Syntax) ---
if __name__ == '__main__':
    # Create a counter that starts at 3 and increments by 2
    c = makeCounter(3, 2)
    
    # Run the counter for 10 steps. 
    # The transduce method in sm.py handles calling start() and step()
    # For a feedback machine, the input list can be None.
    output_sequence = c.transduce([None] * 10)
    
    print "Counter created with makeCounter(3, 2)"
    print "Output sequence:", output_sequence
    # Expected output: [3, 5, 7, 9, 11, 13, 15, 17, 19, 21]
