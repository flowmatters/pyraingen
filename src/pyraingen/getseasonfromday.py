from datetime import date
from numba import njit

## Import the Global Enumeration
from .global_ import seasSummer, seasAutumn, seasWinter, seasSpring

@njit
def getSeasonFromDay(dayOfYear, nDaysCurrYear):
    """Computes the season from the day of the year
    This function returns the season index from the day of the year.
    
    Parameters
    ----------
    dayOfYear : int
        The day of the year from 1 == January first to either
        365 or 366 being December 31st.
    nDaysCurrYear : int
        Number of days in the current year so that we
        know if this is a leap year or not.\n

    Returns
    ----------
    int
        An integer enumeration representing the season.
    """
    #   Dr Peter Brady <peter.brady@wmawater.com.au>
    #   2016-08-15

    #   Caleb Dykman
    #   2021-09-16

    ## Algorithm
    #   1) decide if this is a leap year.
    #   2) compute which month we are in.
    #   3) compute the season from that.

    if nDaysCurrYear == 365:
        if dayOfYear >= 355 or dayOfYear <= 59:
            currentSeason = seasSummer
        elif dayOfYear >= 60 and dayOfYear <= 151:
            currentSeason = seasAutumn
        elif dayOfYear >= 152 and dayOfYear <= 243:
            currentSeason = seasWinter
        else:
             currentSeason = seasSpring
    elif nDaysCurrYear == 366:
        if dayOfYear >= 355 or dayOfYear <= 60:
            currentSeason = seasSummer
        elif dayOfYear >= 61 and dayOfYear <= 152:
            currentSeason = seasAutumn
        elif dayOfYear >= 153 and dayOfYear <= 244:
            currentSeason = seasWinter
        else:
             currentSeason = seasSpring

    return currentSeason




