import lib601.sf as sf
import lib601.optimize as optimize
import operator



# You might want to define, and then use this function to find a good
# value for k2.

# Given k1, return the value of k2 for which the system converges most
# quickly, within the range k2Min, k2Max.  Should call optimize.optOverLine.
def plant1(T):
   FeedbackAdd = sf.FeedbackAdd(sf.Gain(1), sf.R())
   return sf.Cascade(sf.Gain(T),sf.Cascade(sf.R(), FeedbackAdd))


def plant2(T, V):
   FeedbackAdd = sf.FeedbackAdd(sf.Gain(1), sf.R())
   return sf.Cascade(sf.Gain(T*V),sf.Cascade(sf.R(), FeedbackAdd))



def delayPlusPropModel(k1, k2):
    T = 0.1
    V = 0.1

    # Controller:  your code here
    controller = sf.FeedforwardAdd(sf.Gain(k1), sf.Cascade(sf.R(), sf.Gain(k2)))
    # The plant is like the one for the proportional controller.  Use
    # your definition from last week.
    plant1_sys = plant1(T)
    plant2_sys = plant2(T, V)
    total_plant = sf.Cascade(plant1_sys, plant2_sys)
    forward_path = sf.Cascade(controller, total_plant)
    # Combine the three parts
    sys = sf.FeedbackSubtract(forward_path,sf.Gain(1))
    return sys

def bestk2(k1, k2Min, k2Max, numSteps):
    def objective(k2):

        system_function = delayPlusPropModel(k1, k2)
        poles = system_function.poles()

        if not poles:
            return float('inf')

        max_pole_magnitude = max(abs(pole) for pole in poles)
        return max_pole_magnitude

    (bestObjValue, bestK2) = optimize.optOverLine(
        objective,
        k2Min,
        k2Max,
        numSteps,
        operator.lt
    )

    return bestK2



def anglePlusPropModel(k3, k4):
    T = 0.1
    V = 0.1

    # plant 1 is as before
    plant1_sys = plant1(T)
    # plant2 is as before
    plant2_sys = plant2(T, V)
    new_plant1 = sf.FeedbackSubtract(plant1_sys,sf.Gain(k4))
    new_total_plant = sf.Cascade(new_plant1, plant2_sys)
    forward_path = sf.Cascade(sf.Gain(k3), new_total_plant)
    # The complete system
    sys = sf.FeedbackSubtract(forward_path,sf.Gain(1))
    
    return sys


# Given k3, return the value of k4 for which the system converges most
# quickly, within the range k4Min, k4Max.  Should call optimize.optOverLine.

def bestk4(k3, k4Min, k4Max, numSteps):
    def objective(k4):
        system_function = anglePlusPropModel(k3, k4)
        poles = system_function.poles()
        if not poles:
            return float('inf')
        max_pole_magnitude = max(abs(pole) for pole in poles)

        return max_pole_magnitude
    (bestObjValue, bestK4) = optimize.optOverLine(
        objective,
        k4Min,
        k4Max,
        numSteps,
        operator.lt
    )

    return bestK4



def run_optimization_example(k1_test, k2_min, k2_max, num_steps):
    print("--- Optimizing for k1 = %s ---" % k1_test)


    optimal_k2 = bestk2(k1_test, k2_min, k2_max, num_steps)


    optimal_sys = delayPlusPropModel(k1_test, optimal_k2)
    optimal_pole_mag = max(abs(pole) for pole in optimal_sys.poles())


    print("Best k2: %.3f" % optimal_k2)
    print("Dominant Pole Magnitude: %.3f" % optimal_pole_mag)

    return optimal_k2, optimal_pole_mag

def run_optimization_example_2(k3_test, k4_min, k4_max, num_steps):
    print("--- Optimizing for k1 = %s ---" % k3_test)


    optimal_k4 = bestk4(k3_test, k4_min, k4_max, num_steps)


    optimal_sys = anglePlusPropModel(k3_test, optimal_k4)
    optimal_pole_mag = max(abs(pole) for pole in optimal_sys.poles())


    print("Best k4: %.3f" % optimal_k4)
    print("Dominant Pole Magnitude: %.3f" % optimal_pole_mag)

    return optimal_k4, optimal_pole_mag

k1 = 300
k2_min = -400
k2_max = 400
num_steps = 50001
run_optimization_example(k1,k2_min,k2_max,num_steps)

k3 = 30 #1 3 10 30
k4_min = -100
k4_max = 100
num_steps = 50001
#run_optimization_example_2(k3, k4_min, k4_max, num_steps)
