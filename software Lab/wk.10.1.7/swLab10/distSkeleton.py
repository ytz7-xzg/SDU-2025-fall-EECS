"""
Discrete probability distributions
"""

import random
import operator
import copy

import lib601.util as util

class DDist:
    """
    Discrete distribution represented as a dictionary.  Can be
    sparse, in the sense that elements that are not explicitly
    contained in the dictionary are assumed to have zero probability.
    """
    def __init__(self, dictionary):
        self.d = dictionary
        """ Dictionary whose keys are elements of the domain and values
        are their probabilities. """

    def dictCopy(self):
        """
        @returns: A copy of the dictionary for this distribution.
        """
        return self.d.copy()

    def prob(self, elt):
        """
        @param elt: an element of the domain of this distribution
        (does not need to be explicitly represented in the dictionary;
        in fact, for any element not in the dictionary, we return
        probability 0 without error.)
        @returns: the probability associated with C{elt}
        """
        if self.d.has_key(elt):
            return self.d[elt]
        else:
            return 0

    def support(self):
        """
        @returns: A list (in arbitrary order) of the elements of this
        distribution with non-zero probabability.
        """
        return [k for k in self.d.keys() if self.prob(k) > 0]

    def marginalizeOut(self,index):
        #去除一个项，对余下的项概率整合，求出另一个项的具体概率分布
        n_d = {}
        for k in self.support():
            prob = self.prob(k)
            n_key = removeElt(k,index)
            incrDictEntry(n_d,n_key,prob)
        return DDist(n_d)

    def conditionOnVar(self,index,value):
        #在知道结果之后，再重新归一化一遍，才知道某一项的条件概率
        n_d = {}
        total_prob = 0
        for k in self.support():
            if k[index] == value:
                prob = self.prob(k)
                n_key = removeElt(k,index)
                n_d[n_key] = prob
                total_prob += prob
        if total_prob > 0:
            for k in n_d:
                n_d[k] /= total_prob
        return DDist(n_d)


    def __repr__(self):
        if len(self.d.items()) == 0:
            return "Empty DDist"
        else:
            dictRepr = reduce(operator.add,
                              [util.prettyString(k)+": "+\
                               util.prettyString(p)+", " \
                               for (k, p) in self.d.items()])
            return "DDist(" + dictRepr[:-2] + ")"
    __str__ = __repr__


######################################################################
#   Utilities


def removeElt(items, i):
    """
    non-destructively remove the element at index i from a list;
    returns a copy;  if the result is a list of length 1, just return
    the element  
    """
    result = items[:i] + items[i+1:]
    if len(result) == 1:
        return result[0]
    else:
        return result

def incrDictEntry(d, k, v):
    """
    If dictionary C{d} has key C{k}, then increment C{d[k]} by C{v}.
    Else set C{d[k] = v}.
    
    @param d: dictionary
    @param k: legal dictionary key (doesn't have to be in C{d})
    @param v: numeric value
    """
    if d.has_key(k):
        d[k] += v
    else:
        d[k] = v

def JDist(PA,PBgA):
    #求A,B同时发生的概率分布
    joint_dict = {}
    for a in PA.support():
        distB = PBgA(a)
        for b in distB.support():
            prob = PA.prob(a)*distB.prob(b)
            joint_dict[(a,b)] = prob
    return DDist(joint_dict)

def bayesEvidence(PBgA,PA,b):
    #conditionOnVar(1, b): 在联合分布中锁定变量位于index1的B的值为b，归一化后返回条件概率的分布
    return JDist(PA,PBgA).conditionOnVar(1,b)

def totalProbability(PBgA,PA):
    #marginalizeOut(0): 把变量位于index0的A消除，剩下的就是P(B)
    return JDist(PA,PBgA).marginalizeOut(0)
# If you want to plot your distributions for debugging, put this file
# in a directory that contains lib601, and where that lib601 contains
# sig.pyc.  Uncomment all of the following.  Then you can plot a
# distribution with something like:
# plotIntDist(MixtureDist(squareDist(2, 6), squareDist(4, 8), 0.5), 10)

# import lib601.sig as sig

# class IntDistSignal(sig.Signal):
#     def __init__(self, d):
#         self.dist = d
#     def sample(self, n):
#         return self.dist.prob(n)
# def plotIntDist(d, n):
#     IntDistSignal(d).plot(end = n, yOrigin = 0)
