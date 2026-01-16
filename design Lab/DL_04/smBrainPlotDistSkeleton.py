import math
import lib601.sm as sm
from soar.io import io
import lib601.gfx as gfx
import lib601.util as util


DESIRED_DISTANCE = 0.7 # set ideal distance to the wall

class DistanceSensor(sm.SM):
    def __init__(self, initial_distance, num_delays):
        self.startState = [initial_distance] * num_delays #set the initial state to make sure that the output is effective 

    def getNextValues(self, state, _input):
        print("DATA FROM SONAR3:", _input.sonars[3])  #print the third sonar's statistics
        return ([_input.sonars[3]] + state[:-1], state[-1])#add the newest distance and delete the last one 

class DistanceController(sm.SM):
    def __init__(self, gain,max_vel):
        self.gain = gain #set some variables(gain and max_vel)may be should do some changes
        self.max_vel = max_vel#restrict robots 's max speed
    
    def getNextValues(self, state, sensor_input):
        return (state, io.Action(rvel=0, fvel=2*(-DESIRED_DISTANCE + sensor_input)))#return the order ,rotate speed =0 ,foward speed can change according the distance to the wall



brain_sm = sm.Cascade(DistanceSensor(1.5, 1), DistanceController(gain=12,max_vel = 0.5))#ccascade the two state machines and set some fixed numbers
brain_sm.name = 'brainSM'

def plotSonar(sonarNum):
    robot.gfx.addStaticPlotFunction(y=('sonar'+str(sonarNum),
                                 lambda: io.SensorInput().sonars[sonarNum]))

def setup():
    robot.gfx = gfx.RobotGraphics(drawSlimeTrail=False)
    plotSonar(3)
    robot.behavior = brain_sm
    robot.behavior.start(traceTasks = robot.gfx.tasks())

def brainStart():
    pass

def step():
    robot.behavior.step(io.SensorInput()).execute()

def brainStop():
    pass

def shutdown():
    pass

