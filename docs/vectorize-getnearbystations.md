# Vectorization of getnearbystations.py

## Problem

Profiling of the stochastic rainfall service revealed that `regionaliseddailysim` took ~50s per request, with 98% of that time (48.6s) spent in `getnearbystations.station()` — the function that finds the nearest reference stations to a target location.

The Fortran daily rainfall simulation itself took only 0.6s.

## Root Cause

The original implementation used a double-nested Python loop iterating over ~1694 stations and 33 similarity attributes. Each iteration accessed station data via xarray single-element indexing (`stnToUse['LAT'][loopStation]`), which is extremely slow for scalar access because xarray performs label alignment, type checking, and metadata propagation on every indexing operation.

The inner loop computed a logistic regression for each station-attribute pair using `math.exp()` (Python scalar math), resulting in ~55,900 iterations of slow Python code.

A second nested loop (lines 121-125) then normalised and summed the predictor values across all stations and attributes.

## Solution

The computation was replaced with vectorized numpy operations:

1. **Delta computation**: Station deltas (latitude, longitude, elevation, distance-to-coast, temperature) are computed as numpy vectors over all stations simultaneously, using pandas `.values` to extract raw numpy arrays instead of xarray indexing.

2. **Logistic regression**: The predictor matrix (nStations x 7) is multiplied against the coefficient matrix (7 x nAttributes) in a single `np.matmul` operation, followed by a vectorized `np.exp` call for the logistic function.

3. **Normalisation and ranking**: The max-normalisation and summation across attributes uses numpy broadcasting and `np.argpartition` for efficient top-N selection.

4. **Data structures**: The function now works with pandas DataFrames and numpy arrays directly, removing the xarray dependency (`pd.read_csv().to_xarray()` replaced with `pd.read_csv()`).

## Result

| Metric | Before | After |
|---|---|---|
| `find_stations` time | 48.6s | <0.1s |
| `regionaliseddailysim` total | 50.2s | 1.0s |
| Overall request time | ~67s | ~18s |

The output (selected stations, weights, years) is identical.

## Compatibility

The function signature is unchanged. The output file format (`nearby_station_details.out`) is identical. No changes are required in calling code.
