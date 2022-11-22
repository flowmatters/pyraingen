import numpy as np
import os

from .fortran_daily import regionalised_daily
from .get_fortran_data import copy_fortran_data
from .convert_daily_to_NetCDF import convertdailync

def regionaliseddailysim(nyears, startyear, nsim,
                            targetidx, targetlat, targetlon, 
                            targetelev, targetdcoast, targetanrf,
                            data_path, output_path_txt, 
                            netcdf = True, output_path_nc='daily.nc',
                            output_stats="stat_.out", output_val="rev_.out",
                            cutoff=0.30, wind=15, nstation=5, 
                            nlon=3, lag=1, iamt=1, ival=0, irf=1):
    """Front end to the regionalised daily rainfall generator.
    For a detailed description of the approach refer to: 
    Mehrotra et al (2012) "Continuous Rainfall simulation: 2.
    A regionalised daily rainfall generation approach".

    Parameters
    ----------
    nyears : int
        Number of years to be simulatied.
    startyear : int
        Start year of simulation.
    nsim : int
        Number of realisations to be simulated.
    targetidx : int
        Id number of target 'station'. 5 digits.
    targetlat : float
        Latitude of target.
    targetlon : float
        Longitude of target.
    targetelev: float
        Elevation of target in m (AHD).
    targetdcoast : float
        Distance to coast of target in km.
    targetanrf : float
        Annual rainfall at target in mm.
    datapath : str
        Path to historical daily rainfall data. Must not be longer than 72 characters.
    output_path_txt : str
        Name and location for output text file. Must not be longer than 72 characters.
    netcdf : bool
        True for output in netcdf format. False for only text file output.
        Default is True.
    output_path_nc : str
        Name and location for output netcdf.
        Default is 'daily.nc' in working directory.
    output_stats : str
        Name and location for output stats text file. Must not be longer than 72 characters.
        Default is 'stat_.out' in working directory.
    output_val : str
        NB: Currently not supported. Leave as default.
        Name and location for output validation text file. Must not be longer than 72 characters.
        Default is 'rev_.out' in working directory.
    cutoff : float
        Threshold for defining wet and dry days. Days with rainfall above this threshold will be 
        defined as wet and below as dry.
        Default is 0.30.
    wind : int
        half the size of window to search around target day.
        Default is 15 (i.e. search 15 days before and 15 days after).
    nstation : int
        Number of nearby stations to find.
        Default is 5.
    nlon : int
        Leave at default.
        Default is 3.
    lag : int
        Leave at default.
        Default is 1.
    iamt : int
        Leave at default.
        Default is 1.
    ival : int
        NB: Currently not supported. Leave as default.
        Default is 0.
    irf : int
        Leave at default.
        Default is 1. 


    Returns
    ----------
    text file
        Saves text file of daily simulations to specified file path.
    
    netCDF
        if netcdf boolean is True, Saves netCDF of daily simulations to specified file path.    
    """
    
    # Check if file exists
    if os.path.exists("drop.out"):
        os.remove("drop.out")
    
    # Input parameters
    rain = str(cutoff) + ' '
    iband = str(wind)  + ' '
    nstation = str(nstation)  + ' ' 
    nsim = str(nsim)  + ' '
    nlon = str(nlon) + ' ' 
    lag = str(1) + ' '
    ng = str(nyears) + ' '
    nsgtart = str(startyear) + ' '
    iamt = str(iamt) + ' '
    ival = str(ival) + ' '
    irf = str(irf) + ' '
    
    # Target station details
    idx = str(targetidx) + ' '
    lat = str(targetlat) + ' '
    lon = str(targetlon) + ' '
    elev = str(targetelev) + ' '
    dcoast = str(targetdcoast) + ' '
    anrf = str(targetanrf) + ' '

    copy_fortran_data()
    
    # Write paramters into data_r file
    with open("data_r.dat",'r') as file:
        data_r = file.readlines()

    data_r[2] = ' ' + rain + iband + nstation + nsim + nlon + lag + ng + nsgtart + iamt + ival + irf +'\n'
    data_r[10] = ' ' + idx + lat + lon + elev + dcoast + anrf +'\n'
    data_r[12] = data_path +'\n'
    data_r[14] = output_path_txt +'\n'
    data_r[16] = output_stats +'\n'
    data_r[18] = output_val +'\n'

    with open("data_r.dat",'w') as file:
        file.writelines(data_r)

    # Begin simulation
    idrop =-1
    kk = 0
    break_out_flag = False

    while True:
        regionalised_daily.regionalised_daily(idrop=idrop)
        with open('nearby_station_details.out') as file:
            print(file.read())
        nearby = np.genfromtxt('nearby_station_details.out', 
                                skip_header=6, invalid_raise=False) 
        while True:
                try:
                    idrop = int(input("Do you want to drop any nearby station?\nIf yes, enter station sr no otherwise enter zero: " ))
                    if idrop < 0:
                        print("Sorry, no numbers below zero.") 
                    elif idrop > 0:
                        if idrop > 5:
                            print("Sorry, please choose one of the listed nearby station sr nos.")
                        else:
                            kk += 1
                            with open ("drop.out", 'a') as file:
                                file.write(str(int(kk)).rjust(12)
                                            + str(int(nearby[idrop-1][1])).rjust(12)+'\n')
                            idrop = kk
                            break
                    else:
                        regionalised_daily.regionalised_daily(idrop=idrop)
                        break_out_flag = True
                        break
                except ValueError:
                    print("Sorry, invalid input. Please makesure input is integer only.")
        
        if break_out_flag:
            break
    
    if netcdf == True:
        convertdailync(output_path_txt, output_path_nc, startyear, nyears, nsim, missingDay=-999.9)
        #remove textfile
        if os.path.exists(output_path_txt):
            os.remove(output_path_txt)