#3 Convert Daily Simulations to NetCDF
# This is a utility to convert the text files generated from the reference
# implementation FORTRAN 77 into a compressed NetCDF.
#
# Dr Peter Brady <peter.brady@wmawater.com.au>
# 2016-08-24
#
# Caleb Dykman
# 2022-07-14

# Import Packages
import os
import numpy as np
import netCDF4 as nc
from datetime import date
import warnings
warnings.filterwarnings("ignore")

# Import Defined Functions
from datevectojd import datevecToJD
from producedailynetcdf import produceDailyNetCDF

def convertdailync(fnameSRC, fnameTRG, yearStart, nYears, nSims, missingDay = -999.9):
    """Convert Daily Simulations to NetCDF. This is a utility to convert the text files generated from the reference
    implementation FORTRAN 77 into a compressed NetCDF.

    Parameters
    ----------
    fnameSRC : str
        This is the path to the input file.
    fnameTRG : str
        This is the path to the output file.
    yearStart : int
        Start year of data.
    nYears : int
        Number of years of data.
    nSims : int
        Number of simulations.
    missingDay : float
        missing day value. default is -999.9.

    Returns
    ----------
    netCDF
        Saves netCDF of daily simulations to specified file path.    
    """

    ## Check of the file exists
    if os.path.exists(fnameTRG):
        raise Warning('PSDNC:Exists ' + 'The file {}, exists please check the '
        'name and/or delete the file and try again.'.format(fnameTRG))
        status = False
        print(status)

    # # Write To a NetCDF
    # if exist(fnameTRG, 'file')
    #    delete(fnameTRG)
    # end

    ## Allocate RAM
    yearEnd = yearStart + nYears - 1
    dateNumStart = date(yearStart, 1, 1)
    dateNumEnd   = date(yearEnd, 12, 31)
    nDays = (date.toordinal(dateNumEnd)
        - date.toordinal(dateNumStart)+1
    )

    dayVector = np.arange(0,nDays,1)
    dayVector = dayVector + datevecToJD(date(int(yearStart), 1, 1))

    dailyData = np.ones((nDays, nSims)) * missingDay

    with open(fnameSRC) as f:
        for loopReadSims in range(nSims):
            print(f'Reading Simulation: {loopReadSims}')
            for loopReadRain in range(nDays):
                buffer = f.readline().rstrip()
                buffer = np.array(buffer.split()).astype(float)
                dailyData[loopReadRain, loopReadSims] = buffer[-1]
            
            # Read the dummy line and skip on
            f.readline()


    ## Write To a NetCDF
    produceDailyNetCDF(fnameTRG, dailyData, dayVector)