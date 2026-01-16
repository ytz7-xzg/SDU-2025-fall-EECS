"""
Class and some supporting functions for representing and manipulating system functions. 
"""

import math
import lib601.poly as poly
import lib601.util as util


class SystemFunction:
    """
    Represent a system function as a ratio of polynomials in R
    """
    def __init__(self, numeratorPoly, denominatorPoly):
        self.numeratorPoly = numeratorPoly
        self.denominatorPoly = denominatorPoly

    def poles(self):
        r_coeffs = self.denominatorPoly.coeffs
        z_coeffs = r_coeffs[:]
        z_coeffs.reverse()
        z_ploy = poly.Polynomial(z_coeffs)
        return z_ploy.roots()

    def poleMagnitudes(self):
        poles = self.poles()
        return [abs(i) for i in poles]

    def dominantPole(self):
        poles = self.poles()
        return util.argmax(poles,abs)



    def __str__(self):
        return 'SF(' + self.numeratorPoly.__str__('R') + \
               '/' + self.denominatorPoly.__str__('R') + ')'

    __repr__ = __str__


def Cascade(sf1, sf2):
    N1 = sf1.numeratorPoly
    N2 = sf2.numeratorPoly
    D1 = sf1.denominatorPoly
    D2 = sf2.denominatorPoly
    total_numeratorPoly = N1 * N2
    total_denominatorPoly = D1 * D2
    return SystemFunction(total_numeratorPoly, total_denominatorPoly)

def FeedbackSubtract(sf1, sf2=None):
    N1 = sf1.numeratorPoly
    D1 = sf1.denominatorPoly
    if sf2 is None:
        N2 = poly.Ploynomial([1])
        D2 = poly.Ploynomial([1])
    else:
        N2 = sf2.numeratorPoly
        D2 = sf2.denominatorPoly
    total_numeratorPoly = N1*D2
    total_denominatorPoly = N1*N2 + D1*D2
    return SystemFunction(total_numeratorPoly, total_denominatorPoly)

