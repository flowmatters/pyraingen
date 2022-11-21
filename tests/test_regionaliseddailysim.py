from pyraingen.regionaliseddailysim import regionaliseddailysim

nyears = 79
startyear = 1930
nsim = 10
targetidx = 66037 
targetlat = -33.9410 
targetlon = 151.1730 
targetelev = 6.00 
targetdcoast = 0.27 
targetanrf = 1086.71
data_path = "C:/Users/z3460382/daily_data/"
output_path_txt = "mmm_066037.out"

regionaliseddailysim(nyears, startyear, nsim,
                        targetidx, targetlat, targetlon, 
                        targetelev, targetdcoast, targetanrf,
                        data_path, output_path_txt, 
                        netcdf = True, output_path_nc='daily.nc',
                        output_stats="stat_.out", output_val="rev_.out",
                        cutoff=0.30, wind=15, nstation=5, 
                        nlon=3, lag=1, iamt=1, ival=0, irf=1)