from importlib import resources

def get_index():
    """Get path to station index data.

    Returns
    -------
    pathlib.PosixPath
        Path to file.
    """
    with resources.path("pyraingen.data", "index.nc") as f:
        data_file_path = f
    return str(data_file_path)