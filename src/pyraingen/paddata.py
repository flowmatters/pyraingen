# Packages & Libraries
import numpy as np
from datetime import date
#import nvtx

## Global constants
from .global_ import missingDay

#@nvtx.annotate()
def padData(simYearStart, simYearEnd, dayVecStart, dayVecEnd):
    """Pads out the data array to make full years with missingDay values.
    
    Parameters
    ----------
    simYearStart : int
        Start year for simulation.
    simYearEnd : int
        End year for simulation.
    dayVecStart : array
        Vector of year, month, day for start of simulation.
    dayVecEnd :  array
        Vector of year, month, day for end of simulation.\n

    Returns
    ----------
    targetDailyRain : array
        1D array of size nDaysKnown filled with missingDay values.
    dataIdxStart : int 
        Ordinal day Id for start of simulation.
    dataIdxEnd : int
        Ordinal day Id for end of simulation.
    """
    nDaysKnown = (date.toordinal(date(simYearEnd,12,31))
        - date.toordinal(date(simYearStart,1,1))+1)
    targetDailyRain = np.ones((nDaysKnown)) * missingDay
    # Get an index into the tmpDaily array where our known data
    # should start.
    dataIdxStart = (date.toordinal(date(
        int(dayVecStart[0]), int(dayVecStart[1]), int(dayVecStart[2])))
        - date.toordinal(date(simYearStart,1,1)))
    dataIdxEnd = (date.toordinal(date(
        int(dayVecEnd[0]),int(dayVecEnd[1]),int(dayVecEnd[2])))
        - date.toordinal(date(simYearStart,1,1))+1)
    
    return targetDailyRain, dataIdxStart, dataIdxEnd