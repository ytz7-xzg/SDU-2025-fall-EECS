import lib601.dist as dist
import lib601.sm as sm
import lib601.ssm as ssm
import lib601.util as util


def bayesEvidence(state, observation, observationModel):
    posterior_prob = {}
    total_prob = 0
    for s in state.support():
        pOgS = observationModel(s).prob(observation)
        # p(o) = p(s) * p(o | s)
        pS = state.prob(s)
        p = pS * pOgS
        if p>0:
            posterior_prob[s] = p
            total_prob += p
    # p(s | o) = p(o,s)/p(o)
    for s in state.support():
        posterior_prob[s] /= total_prob
    return dist.DDist(posterior_prob)


def totalProbability(state, transitionModel):
    next_prob = {}
    # p(S(t+1)) = p(S(t)) * p(S(t+1) | S(t))
    for s in state.support():
        pS = state.prob(s)
        next_state = transitionModel(s)
        for ns in next_state.support():
            pNSgS = next_state.prob(ns)
            if ns not in next_prob:
                next_prob[ns] = 0
            next_prob[ns] += pNSgS * pS
    return dist.DDist(next_prob)


class StateEstimator(sm.SM):
    def __init__(self, model):
        self.model = model
        self.startState = model.startDistribution

    def getNextValues(self, state, inp):
        (o, i) = inp
        #o是观测 i是转移
        posterior_P = bayesEvidence(state, o, self.model.observationDistribution)
        next_P = totalProbability(posterior_P, self.model.transitionDistribution(i))
        return (next_P, next_P)

# Test

transitionTable = \
   {'good': dist.DDist({'good' : 0.7, 'bad' : 0.3}),
    'bad' : dist.DDist({'good' : 0.1, 'bad' : 0.9})}
observationTable = \
   {'good': dist.DDist({'perfect' : 0.8, 'smudged' : 0.1, 'black' : 0.1}),
    'bad': dist.DDist({'perfect' : 0.1, 'smudged' : 0.7, 'black' : 0.2})}

copyMachine = \
 ssm.StochasticSM(dist.DDist({'good' : 0.9, 'bad' : 0.1}),
                # Input is irrelevant; same dist no matter what
                lambda i: lambda s: transitionTable[s],
                lambda s: observationTable[s])
obs = [('perfect', 'step'), ('smudged', 'step'), ('perfect', 'step')]

cmse = StateEstimator(copyMachine)

print cmse.transduce(obs)


