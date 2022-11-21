import numpy as np
from numba import njit

@njit
def computeSubDailyKDE(sampleSize):
    """This function computes the sub-daily Kernel Density Estimate for a
    given sample size.  It is intended to compute Equation 2 in the paper
    Westra et al 2012, CONTINUOUS RAINFALL: REGIONALIZED DISAGGREGATION
    
    Parameters
    ----------
    sampleSize : int 
        Number of samples that will be selected from.\n

    Returns
    ----------
    array
        A vector of the probability for each sample selected.
    """
    #   Dr Peter Brady <peter.brady@wmawater.com.au>
    #   2016-08-16
    
    #   Caleb Dykman
    #   2021-09-16

    sampleSize = int(sampleSize)
    sampleRange = sampleSize + 1
    
    probVector = np.zeros((sampleSize))
    runSum = float(0)

    for loopComp in range(1, sampleRange):
        probVector[(loopComp-1)] = 1/(loopComp)
        runSum +=probVector[(loopComp-1)]

    probVector[0] = probVector[0] / runSum
    for loopComp in range(1, sampleSize):
        probVector[loopComp] = (probVector[(loopComp-1)] + 
        (probVector[loopComp] / runSum))

    return probVector
