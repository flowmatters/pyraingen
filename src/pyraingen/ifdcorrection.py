import numba
import numpy as np

@numba.jit(nopython=True, parallel=True, cache=True)
def correction(minsPerSample, 
    nSims, 
    currentDur, 
    years, 
    TargetIFDduration, 
    annualMaxIndexLinear, 
    annualMaxSortedIndex, 
    dataRaw_flat,
    dataRaw_nomax_flat, 
    extremeFit, 
    nonExtremeSortedIndex, 
    fnNonEx):
    """Function to correct The Rainfall Sequences
    by multipling rain by its correction factor.

    Parameters
    ----------
    minsPerSample :  int
        Length of base data timestep. Default is 6 min. 
    nSims :  int
        Number of data simulations provided. 
    currentDur : int
        Event duration being corrected.     
    years : array
        Array of the years of data.
    TargetIFDduration : array.
        Vector of target IFD durations to correct.
    annualMaxIndexLinear : array
        Array of linear indexes into array of annual maximum values.
    annualMaxSortedIndex : array
        Array of indexes into sorted annual maximum values.
    dataRaw_flat : array
        Flattened array of raw input rainfall data.
    dataRaw_nomax_flat : array
        Flattened array of raw input rainfall data with annual maximum
        values set to zero.
    extremeFit : array
        Vector of values fitted to extreme polynomial function.
    nonExtremeSortedIndex : array 
        Array of indexes into the sorted non extreme (non annual maximas) 
        rainfall values. 
    fnNonEx : float
        Non-extreme scaling factor.\n

    Returns
    ----------
    array
        Flattened array of corrected rainfall data.
    """
    for loopSim in numba.prange(nSims):
        # NB: this outer loop can not easily be vectorised as the sort
        # indices are not consistend across the third dimension of the
        # rainfall data.
        #
       
        # We can do the non-extreme correction here as its linear index
        # is always relative to the main data array, no conversion is
        # necessary. There can be issues in inadvertently scaling maximum
        # values that have been indexed as non extreme after being zeroed 
        # out in a earlier step. I have created a copy of dataraw with the
        # maximums zeroed out for the non extreme scaling factor to be applied
        # I will do the non extreme scaling first and then add back the scaled 
        # extreme values at the end.

        dataRaw_nomax_flat[nonExtremeSortedIndex[loopSim, :]] = (
            dataRaw_nomax_flat[nonExtremeSortedIndex[loopSim, :]] * fnNonEx
        )
       
        # Also, we only have to handle the extreme locations as the
        # non-extreme indices always map into the full data array.
        #
        # This block of code has been rewritten so that it is only one
        # set that we loop through to simplify the vector sorts.
        #
        # 1) the array stride for the underlying six minute
        # correction.
        correctionStride = TargetIFDduration[currentDur]/minsPerSample
        for loopCorrection in range(len(years)):
            # First "expand" the index from the aggregated index to the
            # underlying six minute time step
            correctionIndexLinear = (
                (annualMaxIndexLinear[loopSim, annualMaxSortedIndex[loopSim, loopCorrection]])
                * TargetIFDduration[currentDur]/minsPerSample
            )
            
            # Now convert it to a stride:
            correctionIndexLinear = (
                np.arange(correctionIndexLinear,correctionIndexLinear+correctionStride,1)
            ).astype(np.int32)

            # Now correct and insert
            dataRaw_nomax_flat[correctionIndexLinear] = (
                dataRaw_flat[correctionIndexLinear] * extremeFit[loopCorrection]
            )
    
    return dataRaw_nomax_flat