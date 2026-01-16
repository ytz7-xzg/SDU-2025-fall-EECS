# -*- coding: utf-8 -*-
import lib601.sig as sig
import lib601.ts as ts
import lib601.sm as sm

######################################################################
##  Make a state machine model using primitives and combinators
######################################################################

def plant(T, initD):
    Feedback_add = sm.FeedbackAdd(sm.R(initD),sm.Gain(1))
    return sm.Cascade(sm.Gain(T),Feedback_add)

def controller(k):
    return sm.Gain(k)

def sensor(initD):
    return sm.R(initD)

def wallFinderSystem(T, initD, k):
    Forward_sm = sm.Cascade(controller(k),plant(T,initD))
    Feedback_sub = sensor(initD)
    return sm.FeedbackSubtract(Forward_sm,Feedback_sub)

# Plots the sequence of distances when the robot starts at distance
# initD from the wall, and desires to be at distance 0.7 m.  Time step
# is 0.1 s.  Parameter k is the gain;  end specifies how many steps to
# plot.

initD = 1.5

def plotD(k, end = 50):
    d = ts.TransducedSignal(sig.ConstantSignal(0.7),
                           wallFinderSystem(0.1, initD, k))
    d.plot(0, end, newWindow = 'Gain ' +str(k))

