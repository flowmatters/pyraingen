# Packages & Libraries
import numpy as np
from datetime import date
from numba.typed import List

# Defined Functions
from .jdtodatevec import jdToDateVec

## Global constants
from .global_ import missingDay
from .global_ import stateBad
from .global_ import ndaysYearLeap
from .global_ import idxfebTwentyNine
from .global_ import stateWetWet, stateWetDry, stateDryWet, stateDryDry


def _build_day_mapping(yearStart, yearEnd, idxYearBase):
    """Build mapping from linear day index to (loopDay, idxYear) for a station."""
    loopDay_list = []
    idxYear_list = []
    for yr_offset in range(yearEnd - yearStart + 1):
        year = yearStart + yr_offset
        is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
        nDays = 366 if is_leap else 365
        for d in range(ndaysYearLeap):
            if d == idxfebTwentyNine and nDays != ndaysYearLeap:
                continue
            loopDay_list.append(d)
            idxYear_list.append(idxYearBase + yr_offset)
    return np.array(loopDay_list, dtype=np.intp), np.array(idxYear_list, dtype=np.intp)


def dailySequences(nSeasons,
                    nYearsPool,
                    stnDetails,
                    nearStationIdx,
                    param,
                    param_path,
                    station_cache=None):
    """Computes the daily sequences.
    Loop through the number of years in the seasonal
    pool and load the daily sequences.

    Parameters
    ----------
    nSeaons : int
        Number of seasons.
    nYearsPool : int
        Number of years in each seasonsal pool.
    stnDetails : dict where keys are words and values are float
        The record of stations from index.txt.  This is
        passed back as it may have changed shape to add according to
        genSeqOption3.
    nearStationIdx : array
        A set of indices into station data for the
        seasonal nearest like stations. This array is nominally two
        dimensional with the first dimension being the seasons and the
        second the number of stations returned.  This is because there
        are possible different correlations between stations over
        different seasons.
    param : dict where keys are words and values are float
        Dictionary of the run parameters.
    param_path : dict where keys are words and values are str
        Dictionary of the necessary paths.\n

    Returns
    ----------
    dailyDepth : list
        A list of arrays (one for each season) containing the daily depth sequences.
    dailyWetState : list
        A list of arrays (one for each season) containing the daily wetState sequences.
    """
    dailyDepth = List()
    dailyWetState = List()
    dryWetCutoff = param['dryWetCutoff']

    for loopSeason in range(nSeasons):
        # Allocate RAM for this daily series:
        nYears = int(nYearsPool[loopSeason].item())
        dailyDepth.append(np.ones(
            (ndaysYearLeap,
            nYears))
            *missingDay)
        dailyWetState.append(np.ones(
            (ndaysYearLeap,
            nYears))
            *stateBad)

        depth_s = dailyDepth[loopSeason]
        wetState_s = dailyWetState[loopSeason]

        #Counter through the year dimension of our arrays
        idxYear = 0

        for loopStation in range(nearStationIdx[0,:].size):
            # Grab a conveniance variable:
            currStnIndex = int(nearStationIdx[loopSeason, loopStation])

            if currStnIndex == 0:
            # There are no more stations for this season
                break

            # Get the start and end years from the NetCDF then compute the
            # number of years in the sequence.
            stnIdx = int(stnDetails['stnIndex'][currStnIndex])
            if station_cache is not None:
                daySeries, rainfall_data = station_cache.get(stnIdx)
                fnameNC = station_cache.filename(stnIdx)
            else:
                import netCDF4 as nc
                fnameNC = ('{}/plv{:06}.nc'.format(param_path['pathSubDaily'], stnIdx))
                ds=nc.Dataset(fnameNC)
                daySeries = ds['day'][:].data
                rainfall_data = ds['rainfall'][:].data
            print('Processing station:', fnameNC)
            dayVecStart = jdToDateVec(daySeries[0])
            dayVecEnd = jdToDateVec(daySeries[-1])
            yearStart = int(dayVecStart[0])
            yearEnd = int(dayVecEnd[0])
            nYearsStation = yearEnd - yearStart + 1

            # Pad out the data array to make full years with missingDay values.
            nDaysKnown = (date.toordinal(date(yearEnd,12,31))
                - date.toordinal(date(yearStart,1,1))+1)
            tmpDaily = np.full(nDaysKnown, missingDay)
            dataIdxStart = (date.toordinal(date(
                int(dayVecStart[0]), int(dayVecStart[1]), int(dayVecStart[2])))
                - date.toordinal(date(yearStart,1,1)))
            dataIdxEnd = (date.toordinal(date(
                int(dayVecEnd[0]),int(dayVecEnd[1]),int(dayVecEnd[2])))
                - date.toordinal(date(yearStart,1,1))+1)

            # Sum sub-daily timesteps to get daily totals.
            # rainfall_data has shape (1, nDays, 240); sum over subday axis
            tmpDaily[dataIdxStart:dataIdxEnd] = (rainfall_data / 10).sum(axis=2).ravel()

            # Build mapping from linear day index to (loopDay, idxYear)
            loopDay_arr, idxYear_arr = _build_day_mapping(yearStart, yearEnd, idxYear)

            # Store daily depths for all days at once
            depth_s[loopDay_arr, idxYear_arr] = tmpDaily

            # Vectorized 3-day sliding window for wet state computation.
            # Yesterday is previous calendar day (0 for very first day).
            # Tomorrow is next calendar day (0 for very last day).
            yesterday_vals = np.empty(nDaysKnown)
            yesterday_vals[0] = 0
            yesterday_vals[1:] = tmpDaily[:-1]

            tomorrow_vals = np.empty(nDaysKnown)
            tomorrow_vals[-1] = 0
            tomorrow_vals[:-1] = tmpDaily[1:]

            # Good data: all three days non-negative (within floating point tolerance)
            good_mask = (
                (yesterday_vals >= -np.spacing(np.abs(yesterday_vals))) &
                (tmpDaily >= -np.spacing(np.abs(tmpDaily))) &
                (tomorrow_vals >= -np.spacing(np.abs(tomorrow_vals)))
            )

            # Vectorized wet state classification
            y_wet = yesterday_vals > dryWetCutoff
            t_wet = tomorrow_vals > dryWetCutoff

            wet_states = np.full(nDaysKnown, stateBad)
            wet_states[good_mask & y_wet & t_wet] = stateWetWet
            wet_states[good_mask & y_wet & ~t_wet] = stateWetDry
            wet_states[good_mask & ~y_wet & t_wet] = stateDryWet
            wet_states[good_mask & ~y_wet & ~t_wet] = stateDryDry

            wetState_s[loopDay_arr, idxYear_arr] = wet_states

            idxYear += nYearsStation

    return dailyDepth, dailyWetState