import os
import numpy as np
import netCDF4 as nc
import datetime

def produceSubDailyNetCDF(fnameNC,subDailyData,dayVector,**kwargs):
    """Creates from scratch a sub-daily netCDF as per schema
    This function is a single write point for sub-daily data. That way we have a 
    consistent layout across all code and a standardised netCDF layout.

    Parameters
    ----------
    fnameNC : str
        The name of the netCDF file to dump data into.  If the
        file exists, a warning will be thrown and the fuction return an
        error.
    subDailyData : array
        An array of the sub-daily with the following
        dimension lengths:\n
            1) number of records per day\n
            2) number of days\n
            3) number of simulations\n
        For BoM or other "real" data, as opposed to simulated data, the
        simulation dimension will == 1.  Data may be padded with BoM or
        similar negative numbers.
    dayVector : array
        A vector of Julian dates for the day of the
        measurement recording.  Remember that Julian days start at
        midday.  No timezone information is stored.
    title : str
        (optional) Data set title to be inserted into the global attribute
        "title".  Default: "Sub-Daily Rainfall".
    institution : str
        (optional) A text field to identify the institution that
        created this data set in the global attribute "institution".
        Default:
            "UNSW Water Research Centre"\n

    Returns
    ----------
    bool
        true for OK, false for an error. 
    """
    #   Dr Peter Brady <peter.brady@wmawater.com.au>
    #   2016-08-26
    #
    #  Caleb Dykman
    #  2021-09-27

    ## Check of the file exists
    if os.path.exists(fnameNC):
        raise Warning('PSDNC:Exists ' + 'The file {}, exists please check the '
        'name and/or delete the file and try again.'.format(fnameNC))
        status = False
        return status
    
    ## Set some defaults
    status = True
    dataSetTitle = 'Sub-Daily Rainfall'
    dataSetInstitution = 'UNSW Water Research Centre'
    nRecordsPerDay = np.size(subDailyData, axis=0)

    ## Get Some Metadata
    # First find the revision.  NB: this uses Subversion keywords.  Do not
    # change the following two lines.
    # revText = '$Revision:: 200   $'
    # headURLText = '$HeadURL: https://develop.wmawater.com.au/svn/arr_p4/branches/pb_working/utils/produceSubDailyNetCDF.m $';
    # revision = sscanf(revText(12:1:18), '%d');
    # headURL = sscanf(headURLText, '$HeadURL: %s$');
    # [~, username] = system('whoami');
    # username = username(1:1:(end-1));
    # pcinfo=java.net.InetAddress.getLocalHost;
    # hostname = char(pcinfo.getHostName);

    # Unpack the kwargs
    if len(kwargs) > 0:
        for key in kwargs.keys():
            if key.lower() == 'title':
               dataSetTitle = kwargs[key] 

            if key.lower() == 'institution':
               dataSetInstitution = kwargs[key]  

    ## Create the Sub-Day Vector
    deltaT = 1 / nRecordsPerDay
    subDayVec = np.arange(deltaT, 1+deltaT, deltaT)

    ## Now Write
    # Create NetCDF
    SubDailync = nc.Dataset(fnameNC, 'w', format='NETCDF4')
   
    # Define Dimensions
    SubDailync.createDimension('day',len(dayVector))
    SubDailync.createDimension('subday', len(subDayVec))
    SubDailync.createDimension('simulation',
        np.size(subDailyData,axis=2)
        )
    
    
    # Create Variables
    days = SubDailync.createVariable('day','f8',('day',),zlib=True,
        complevel=9, shuffle=True
    )
    subdays = SubDailync.createVariable('subday','f8',('subday',),
        zlib=True, complevel=9, shuffle=True, 
    )
    rainfalls = SubDailync.createVariable('rainfall','f4',
        ('subday','day','simulation',), zlib=True, complevel=9, 
        shuffle=True, fill_value=-999.9
    )

    ## Writing Data
    days[:] = dayVector
    subdays[:] = subDayVec
    rainfalls[:,:,:] = subDailyData

    ## Add Attributes
    # Global
    SubDailync.title = dataSetTitle
    SubDailync.history = 'Generated {} by {}@{}'.format(datetime.datetime.now()
        ,'username','hostname'
    )
    SubDailync.source = 'Python function: {}@{}'.format(
        'headURL','revision'
    )
    SubDailync.institution = dataSetInstitution
    SubDailync.conventions = 'ARR Project 4'
    
    # Variable
    days.units = 'Julian date, no timezone, 1900-01-01 00:00:00 == 2415020.5'
    days.long_name = 'Julian Date'
    subdays.units = 'Julian date, no timezone, 1900-01-01 00:00:00 == 2415020.5'
    subdays.long_name = 'Julian Date'
    subdays.description = 'fractional time of day that when added to day gives the time of the rainfall'
    rainfalls.units = 'mm'
    rainfalls.long_name = 'Subdaily Rainfall'

    SubDailync.close()

    return status














