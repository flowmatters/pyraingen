import numpy as np
import pandas as pd
from importlib import resources


def station(param, target, nAttributes=33, fout='nearby_station_details.out'):
    """Algorithm for finding nearby daily stations.

    Parameters
    ----------
    param : dict
        parameter dictionary requiring 'nNearStns',
        'pathStnData', 'pathModelCoeffs', 'pathDailyData'.
    target : dict
        target data dictionary requiring 'index',
        'lat', 'lon', 'elevation', 'distToCoast', and
        'annualRainDepth'.
    nAttributes : int
        Number of attributes of similarity. Leave as default.
        default = 33.
    fout : str
        Path to save output. Leave as default.
        Default is 'nearby_station_details.out'.

    Returns
    ----------
    str
        Prints nearby daily stations.
        Saves text file of nearby daily stations
        to specified file path.
    """
    ## Read the Station Data
    if param['pathStnData'] == None:
        with resources.path("pyraingen.data", "stn_record.csv") as f:
            param['pathStnData'] = str(f)
    stnDf = pd.read_csv(param['pathStnData'])

    # Check if our target station is within the data set.  If it is then its
    # correlation will be perfect and we want to exclude it.
    canUseStation = np.ones(len(stnDf), dtype=bool)
    if target['index'] in stnDf['INDEX'].values:
        canUseStation[stnDf['INDEX'] == target['index']] = False

        # As per the original F77 source, also exclude any stations such that:
        #   abs(deltaLon) < 0.001 AND abs(deltaLat) < 0.001
        too_close = (
            (stnDf['LON'].values - target['lon'] < 0.001) &
            (stnDf['LAT'].values - target['lat'] < 0.001)
        )
        canUseStation[too_close] = False

    ## Reduce Our Station List
    stnToUse = stnDf[canUseStation].reset_index(drop=True)

    ## Read the Coefficients Data
    if param['pathModelCoeffs'] == None:
        with resources.path("pyraingen.data", "daily_logreg_coefs.csv") as f:
            param['pathModelCoeffs'] = str(f)
    modelCoeffs = pd.read_csv(param['pathModelCoeffs']).values.T  # shape: (nAttributes, 7)

    ## Vectorized predictor computation
    # Compute deltas as vectors over all stations
    deltaLat = np.abs(target['lat'] - stnToUse['LAT'].values)
    deltaLon = np.abs(target['lon'] - stnToUse['LON'].values)
    deltaDistToCoast = (np.abs(target['distToCoast'] - stnToUse['DIST_COAST'].values)
                        / ((target['distToCoast'] + stnToUse['DIST_COAST'].values) / 2))
    deltaElevation = (np.abs(target['elevation'] - stnToUse['ELEVATION'].values)
                      / ((target['elevation'] + stnToUse['ELEVATION'].values) / 2))
    deltaLatLon = deltaLat * deltaLon
    deltaTemp = np.abs(target['temp'] - stnToUse['av_an_tmax'].values)

    # Build predictor matrix: (nStations, 7) — intercept + 6 delta terms
    nStations = len(stnToUse)
    predictors = np.column_stack([
        np.ones(nStations),
        deltaLat,
        deltaLon,
        deltaLatLon,
        deltaDistToCoast,
        deltaElevation,
        deltaTemp,
    ])  # shape: (nStations, 7)

    # Logistic function applied as matrix multiply: (nStations, 7) @ (7, nAttributes) -> (nStations, nAttributes)
    linear = predictors @ modelCoeffs[:, :7].T  # modelCoeffs shape: (nAttributes, 7)
    invPredictor = 1.0 / (1.0 + np.exp(-linear))

    ## Compute combined predictor values
    # Normalise each attribute by its maximum, then average across attributes
    invPredMax = invPredictor.max(axis=0)  # shape: (nAttributes,)
    pValue = (invPredictor / invPredMax).sum(axis=1) / nAttributes  # shape: (nStations,)

    # Sort descending and get top stations
    topN = param['nNearStns']
    topIdx = np.argpartition(-pValue, topN)[:topN]
    topIdx = topIdx[np.argsort(-pValue[topIdx])]

    ## Compute the Station Weights
    topPValues = pValue[topIdx]
    stnWeight = topPValues / topPValues.sum()

    nearbyStn = {
        'stnIndex': stnToUse['INDEX'].values[topIdx].tolist(),
        'weight': stnWeight.tolist(),
        'nYears': stnToUse['NYEAR'].values[topIdx].tolist(),
        'avAnRain': stnToUse['AN_RAINFALL'].values[topIdx].tolist(),
        'startYear': [],
    }

    ## Read Start year from file
    for i in nearbyStn['stnIndex']:
        with open(param['pathDailyData'] + f'rev_dr{i:06d}.txt') as f:
            nstart = int(f.readline()[43:47])
        nearbyStn['startYear'].append(nstart)

    ## Write nearby station details file
    with open(fout, 'w') as f:
        f.write('    No Index Weight Years St_year Av annual rainfall\n')
        f.write('\n')
        f.write(' target Station\n')
        f.write(f"     0 {target['index']}  1.000     0    -1   {target['annualRainDepth']}\n")
        f.write('\n')
        f.write(' Nearby Stations\n')
        for loopwrite in range(topN):
            f.write('%6d%6d%7.3f%6d%6d%10.2f\n' %
                (loopwrite+1,
                nearbyStn['stnIndex'][loopwrite],
                nearbyStn['weight'][loopwrite],
                nearbyStn['nYears'][loopwrite],
                nearbyStn['startYear'][loopwrite],
                nearbyStn['avAnRain'][loopwrite])
        )

    ## Print nearby station details
    print('    No Index Weight Years St_year Av annual rainfall')
    print(' target Station')
    print(f"     0 {target['index']}  1.000     0    -1   {target['annualRainDepth']}")
    print(' Nearby Stations')
    for loopprint in range(topN):
        print('%6d%6d%7.3f%6d%6d%10.2f' %
            (loopprint+1,
            nearbyStn['stnIndex'][loopprint],
            nearbyStn['weight'][loopprint],
            nearbyStn['nYears'][loopprint],
            nearbyStn['startYear'][loopprint],
            nearbyStn['avAnRain'][loopprint])
    )
    print()
