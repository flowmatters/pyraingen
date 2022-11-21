import numpy as np

def readCoefficients(pathSRC):
    """Reads the model coefficients from a data file.
    This function reads the data from the coefficients.dat file and
    returns them in an array structure for the rest of the code.  The
    coefficients are used in the logistic regression model of Westra et al
    2012 equations 9 and 10.

    The model coefficient array has three dimensions, namely:\n
        1) length 4: number of seasons in a year, in order they are: Summer
        (DJF); Autumn (MAM); Winter (JJA) and Spring (SON).\n

        2) length 7: the six model coefficients in order they are:\n
                1) Intercept\n
                2) Latitude\n
                3) Longitude\n
                4) Lat x Lon\n
                5) Distance to coast\n
                6) Elevation\n
                7) Temperature\n
                
        3) length 4: the four subdaily rainfall attributes within the
        model, namely:\n
                1) 6 minute intensity\n
                2) 1 hour intensity\n
                3) Fraction of zeros\n
                4) 6 minute time\n
        See Table 2 in the paper for a full list and description.\n

    Parameters
    ----------
    pathSRC : str
        Path to the data directory that contains
        coefficients.dat.\n

    Returns
    ----------
    array
        A three dimensional array that holds the model
        coefficients.
    """
    #   Dr Peter Brady <peter.brady@wmawater.com.au>
    #   2016-08-10

    #   Caleb Dykman
    #   2021-09-16

    ## Import the Globals
    from .global_ import nAttributes, nVariables

    cols = range(1,nAttributes+1,1)

    ## Now Read
    DJF = np.loadtxt((pathSRC),skiprows=2, max_rows=nVariables, usecols=cols)
    MAM = np.loadtxt((pathSRC),skiprows=2+(nVariables+1), max_rows=nVariables, usecols=cols)
    JJA = np.loadtxt((pathSRC),skiprows=2+2*(nVariables+1), max_rows=nVariables, usecols=cols)
    SON = np.loadtxt((pathSRC),skiprows=2+3*(nVariables+1), max_rows=nVariables, usecols=cols)

    modelCoeffs = np.array([DJF, MAM, JJA, SON])

    return modelCoeffs


