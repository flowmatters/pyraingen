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
from .global_ import recordsPerDay


def _build_day_mapping(yearStart, yearEnd, idxYearBase):
    """Build mapping from linear day index to (loopDay, idxYear) for a station.

    Returns arrays of loopDay and idxYear values, one entry per calendar day.
    """
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


def getFragments(nSeasons, nGoodDays, dailyWetState, dailyDepth, stnDetails, nearStationIdx, param, param_path, station_cache=None):
    """Loops over the stations and load and store only the fragments whose
    wetstate != 0 (i.e. some possibly good data).

    Parameters
    ----------
    nSeaons : int
        Number of seasons.
    nGoodDays : array
        Number of good days per year per day per season.
        A "good day" is one that is not of state bad and has
        a depth greater than the dryWetCutoff.
    dailyDepth : list
        A list of arrays (one for each season) containing the daily depth sequences.
    dailyWetState : list
        A list of arrays (one for each season) containing the daily wetState sequences.
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
    fragments : list
        A list of arrays (one for each season) containing a count
        of the number of good fragments available for sampling.
    fragmentsState : list
        A list of arrays (one for each season) containing the daily wetState sequences
        of the good fragments available for sampling.
    fragmentsDailyDepth : list
        A list of arrays (one for each season) containing the daily depth sequences
        of the good fragments available for sampling.
    """

    # Allocate RAM
    fragments = List()
    fragmentsState = List()
    fragmentsDailyDepth = List()

    dryWetCutoff = param['dryWetCutoff']

    for loopSeason in range(nSeasons):
        # Append Season Array to list
        maxNGoodDays = int(np.max(nGoodDays[loopSeason]))
        fragments.append(
            np.zeros((ndaysYearLeap, maxNGoodDays, recordsPerDay)))
        fragmentsState.append(
            np.zeros((ndaysYearLeap, maxNGoodDays)))
        fragmentsDailyDepth.append(
            np.zeros((ndaysYearLeap, maxNGoodDays)))
        fragmentCounter = np.zeros(ndaysYearLeap, dtype=np.intp)

        # Get references to this season's output arrays
        frag_s = fragments[loopSeason]
        fragState_s = fragmentsState[loopSeason]
        fragDepth_s = fragmentsDailyDepth[loopSeason]
        wetState_s = dailyWetState[loopSeason]
        depth_s = dailyDepth[loopSeason]

        #Counter through the year dimension of our arrays
        idxYear = 0
        for loopStation in range(nearStationIdx[0,:].size):
            # Grab a convenience variable:
            currStnIndex = int(nearStationIdx[loopSeason, loopStation])
            if currStnIndex == 0:
                # There are no more stations for this season
                break

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
            dayVecStart = jdToDateVec(daySeries[0])
            dayVecEnd = jdToDateVec(daySeries[-1])
            yearStart = int(dayVecStart[0])
            yearEnd = int(dayVecEnd[0])
            nYearsStation = yearEnd - yearStart + 1

            # As per above, we need to pad out to Jan 1 and Dec 31.
            nDaysKnown = (date.toordinal(date(yearEnd,12,31))
                - date.toordinal(date(yearStart,1,1))+1)
            # Get an index into the SubDaily array where our known data
            # should start.
            dataIdxStart = (date.toordinal(date(
                int(dayVecStart[0]),int(dayVecStart[1]),int(dayVecStart[2])))
                - date.toordinal(date(yearStart,1,1)))
            dataIdxEnd = (date.toordinal(date(
                int(dayVecEnd[0]),int(dayVecEnd[1]),int(dayVecEnd[2])))
                - date.toordinal(date(yearStart,1,1))+1)
            SUBDAILY_SCALE=0.1
            tmpSubDaily = np.ones((nDaysKnown, recordsPerDay,)) * missingDay
            if station_cache is not None:
                tmpSubDaily[dataIdxStart:dataIdxEnd, :] = rainfall_data * SUBDAILY_SCALE
            else:
                tmpSubDaily[dataIdxStart:dataIdxEnd, :] = ds['rainfall'][:].data * SUBDAILY_SCALE

            # Build mapping from linear day index to (loopDay, idxYear)
            loopDay_arr, idxYear_arr = _build_day_mapping(yearStart, yearEnd, idxYear)

            # Vectorized condition checks over all days at once
            subdaily_has_missing = tmpSubDaily.min(axis=1) < 0  # shape: (nDaysKnown,)
            daily_bad_arr = wetState_s[loopDay_arr, idxYear_arr] == stateBad
            day_is_wet_arr = depth_s[loopDay_arr, idxYear_arr] > dryWetCutoff

            # Warn about missing subdaily data for wet, non-bad days
            warn_mask = subdaily_has_missing & day_is_wet_arr & ~daily_bad_arr
            if warn_mask.any():
                warn_indices = np.where(warn_mask)[0]
                for wi in warn_indices:
                    num_missing = int(np.sum(tmpSubDaily[wi] < 0))
                    yr = yearStart + int(np.searchsorted(
                        np.cumsum([366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
                                   for y in range(yearStart, yearEnd + 1)]),
                        wi, side='right'))
                    print(f'{fnameNC}: Missing sub-daily data found for year {yr}, '
                          f'day {loopDay_arr[wi]}: {num_missing} timesteps')

            # Good fragments: wet, not missing, not bad
            good_mask = day_is_wet_arr & ~subdaily_has_missing & ~daily_bad_arr
            good_indices = np.where(good_mask)[0]

            if good_indices.size > 0:
                good_loopDays = loopDay_arr[good_indices]
                good_idxYears = idxYear_arr[good_indices]

                # Sanity check: subdaily sum should match daily depth
                good_sums = tmpSubDaily[good_indices].sum(axis=1)
                good_depths = depth_s[good_loopDays, good_idxYears]
                bad_check = np.abs(good_sums - good_depths) > 1
                if bad_check.any():
                    first_bad = np.where(bad_check)[0][0]
                    gi = good_indices[first_bad]
                    raise ValueError(
                        f'Sum fail for day {good_loopDays[first_bad]}. '
                        f'sum_check: {good_sums[first_bad]}, '
                        f'dailyDepth: {good_depths[first_bad]}')

                # Batch-copy qualifying fragments, grouped by day-of-year
                # Sort by loopDay for efficient scatter
                order = np.argsort(good_loopDays, kind='stable')
                sorted_days = good_loopDays[order]
                sorted_linear = good_indices[order]
                sorted_idxYears = good_idxYears[order]

                unique_days, counts = np.unique(sorted_days, return_counts=True)
                pos = 0
                for d, c in zip(unique_days, counts):
                    start = fragmentCounter[d]
                    end = start + c
                    lin_idx = sorted_linear[pos:pos+c]
                    frag_s[d, start:end, :] = tmpSubDaily[lin_idx, :]
                    fragState_s[d, start:end] = wetState_s[d, sorted_idxYears[pos:pos+c]]
                    fragDepth_s[d, start:end] = depth_s[d, sorted_idxYears[pos:pos+c]]
                    fragmentCounter[d] = end
                    pos += c

            idxYear += nYearsStation

    return fragments, fragmentsState, fragmentsDailyDepth