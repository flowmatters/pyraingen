import numpy as np
from numba import njit

from .global_ import stateWetWet, stateWetDry, stateDryWet, stateDryDry

@njit
def getWetState(rainfallDepth, dryWetCutoff):
    """For a given block of three rainfall depths return the wet/dry
    This function converts a given three day set of daily read rainfall
    depths into a wetness state variable.  It assumes that there is four
    globals for:\n
        1 == WetWet\n
        2 == WetDry\n
        3 == DryWet\n
        4 == DryDry\n
    
    It assumes that all days a "good", i.e. no -888 values.
    
    Parameters
    ----------
    rainfallDepth : 1D array of length 3
        Three day set of daily read rainfall depths.
    dryWetCutoff : float
        Threshold for determining whether a dat is wet or dry.
        default is 0.3 mm. \n

    Returns
    ----------
    int
        Enumerated wetness state variable.
    """
    #   Caleb Dykman
    #   2021-09-15

    ## Logic
    if rainfallDepth[0] > dryWetCutoff and rainfallDepth[2] > dryWetCutoff:
        wetState = stateWetWet
    elif (rainfallDepth[0] > dryWetCutoff and rainfallDepth[2] <= 
    (dryWetCutoff + np.spacing(dryWetCutoff))):
        wetState = stateWetDry
    elif (rainfallDepth[0] <= (dryWetCutoff + np.spacing(dryWetCutoff)) and 
    rainfallDepth[2] > dryWetCutoff):
        wetState = stateDryWet
    else:
        wetState = stateDryDry

    return wetState


