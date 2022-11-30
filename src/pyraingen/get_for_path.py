from importlib import resources

def get_for_path():
    """Get path to the regionalised daily fortran file.

    Returns
    -------
    pathlib.PosixPath
        Path to file.
    """
    with resources.path("pyraingen.fortran_daily", "regionalised_daily.for") as f:
        data_file_path = f
    return str(data_file_path)