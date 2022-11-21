"""Global Constants
"""
## Global constants
# For a detailed description of these three variables see the function
# targetStations in conjunction with the paper Westra et al 2012.
# Number of seasons that we are forcing in this simulation.
nSeasons = 4
# the number of attributes in the logisitic regression.
nAttributes = 4
# The number of variables in the logistic regression.
nVariables = 7

# Season enumerations for the sub-daily code.
# 0 indexed for Python
seasSummer = 0
seasAutumn = 1
seasWinter = 2
seasSpring = 3

# NB: equivalents for the daily code.  These should really be standardised:
# seasSummer = 4
# seasAutumn = 1
# seasWinter = 2
# seasSpring = 3

# Missing data value:
missingDay = -999.9

# Wet Dry enumeration
stateWetWet = 1
stateWetDry = 2
stateDryWet = 3
stateDryDry = 4
stateBad    = 0

# Days in the year
ndaysYearLeap = 366
ndaysYear = 365

# February 29th
# We know that February 29th is always the 60th day of a leap year
#febTwentyNine = 60 #Matlab
idxfebTwentyNine = 59 #Python 

# Sub-daily records
recordsPerDay = 240

# Enum for the three element working day arrays
# 0 indexed for Python
yesterday = 0
today     = 1
tomorrow  = 2