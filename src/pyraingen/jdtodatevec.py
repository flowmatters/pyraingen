import numpy as np
import math
from numba import njit

@njit
def jdToDateVec(julianDate):
    """Converts a Julian Date to a Gregorian Date vector.
    Convert a Julian Date to its corresponding Gregorian calendar date.
    There is no timezone support.
    
    NB: Julian days start not at midnight but midday.
    
    This implementation is based on the routines described in Numerical
    Recipies in Fortran 90 and Duffett-Smith, P. (1992). Practical 
    Astronomy with Your Calculator. Cambridge University Press, England:
    pp. 8,9.
    
    Parameters
    ----------
    julianDate : float
        Julian Date.\n

    Returns
    ----------
    gregorianDateVec : 1D array
        A vector whos elements are:\n
            -) year     (integer)\n
            -) month    (integer)\n
            -) day      (integer)
    """
    #   Dr Peter Brady <peter.brady@wmawater.com.au>
    #   2016-08-26
    #
    #  Caleb Dykman 
    #  22-09-2021

    gregorianDateVec = np.zeros((1, 3))

    julianDate = julianDate + 0.5
    
    I = int(julianDate)
    F = julianDate - I
    
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
        
    C = B + 1524
    
    D = math.trunc((C - 122.1) / 365.25)
    
    E = math.trunc(365.25 * D)
    
    G = math.trunc((C - E) / 30.6001)
    
    day_dec = C - E + F - math.trunc(30.6001 * G)
    
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715

    
    day = int(day_dec)
    #frac_days = day_dec - day

    # hours = frac_days * 24.
    # hours, hour = math.modf(hours)

    
    # mins = hours * 60.
    # mins, min = math.modf(mins)
    
    # secs = mins * 60.
    # secs, sec = math.modf(secs)
    
    # micro = round(secs * 1.e6)

    gregorianDateVec[0][0] = int(year)
    gregorianDateVec[0][1] = int(month)
    gregorianDateVec[0][2] = int(day)
    # gregorianDateVec[0][3] = int(hour)
    # gregorianDateVec[0][4] = int(min)
    # gregorianDateVec[0][5] = float(sec)

    return gregorianDateVec[0]



