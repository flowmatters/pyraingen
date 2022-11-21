# Packages & Libraries
import numpy as np
from numba import njit
#import nvtx

## Global constants
from .global_ import stateBad
from .global_ import ndaysYearLeap

#@nvtx.annotate()
@njit
def maxGoodDays(nSeasons, nYearsPool, dailyWetState, dailyDepth, param):
    """Determines the maximum number of good days per year, per day, per season.
    For this computation a "good day" is one that is not of state bad and has
    a depth greater than the dryWetCutoff.

    Parameters
    ----------
    nSeaons : int
        Number of seasons.
    nYearsPool : array
        Number of years in each seasonsal pool.
    dailyWetState : List
        A list of arrays (one for each season) containing the daily wetState sequences.
    dailyDepth : List
        A list of arrays (one for each season) containing the daily depth sequences.
    param : dict where keys are words and values are float
        Dictionary of the run parameters.\n

    Returns
    ----------
    array
        Number of good days per year per day per season.
        A "good day" is one that is not of state bad and has
        a depth greater than the dryWetCutoff.
    """
    nGoodDays = np.zeros((nSeasons, ndaysYearLeap))
    for loopSeason in range(nSeasons):
        for loopDay in range(ndaysYearLeap):
            for loopYear in range(int(nYearsPool[loopSeason][0])):
                if (dailyWetState[loopSeason][loopDay,loopYear] 
                    != stateBad and 
                    dailyDepth[loopSeason][loopDay,loopYear]
                    > param['dryWetCutoff']):
                    nGoodDays[loopSeason,loopDay] += 1
    return nGoodDays
