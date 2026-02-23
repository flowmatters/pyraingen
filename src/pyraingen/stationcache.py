"""Cache for station NetCDF data to avoid repeated file reads within a single run."""
import netCDF4 as nc


class StationCache:
    """Reads and caches station NetCDF data (day and rainfall arrays).

    Each station file is read at most once. The cache is intended to be
    created per-request and discarded afterwards.
    """

    def __init__(self, subdaily_path, stn_indices):
        """
        Parameters
        ----------
        subdaily_path : str
            Path to subdaily station data directory.
        stn_indices : list
            Station index numbers used to construct filenames.
        """
        self._subdaily_path = subdaily_path
        self._cache = {}

    def get(self, stn_index):
        """Return (day_data, rainfall_data) for a station, reading from disk only once."""
        if stn_index not in self._cache:
            fnameNC = '{}/plv{:06}.nc'.format(self._subdaily_path, int(stn_index))
            ds = nc.Dataset(fnameNC)
            day_data = ds['day'][:].data
            rainfall_data = ds['rainfall'][:].data
            ds.close()
            self._cache[stn_index] = (day_data, rainfall_data)
        return self._cache[stn_index]

    def filename(self, stn_index):
        """Return the NetCDF filename for a station index."""
        return '{}/plv{:06}.nc'.format(self._subdaily_path, int(stn_index))
