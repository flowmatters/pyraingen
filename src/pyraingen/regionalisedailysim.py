import numpy as np
import os

from .fortran_daily import regionalised_daily
from .convert_daily_to_NetCDF import convertdailync

def regionalisedsubdailysim(nyears, startyear, nsim,
                            targetidx, targetlat, targetlon, 
                            targetelev, targetdcoast, targetanrf,
                            data_path, output_path_txt, 
                            netcdf = True, output_path_nc='daily.nc',
                            output_stats="stat_.out", output_val="rev_.out",
                            cutoff=0.30, wind=15, nstation=5, 
                            nlon=3, lag=1, iamt=1, ival=0, irf=1):
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