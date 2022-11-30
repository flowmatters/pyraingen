from importlib import resources

def get_coeffs():
    """Get path to logistic regression coefficients for selecting nearby stations.

    Returns
    -------
    pathlib.PosixPath
        Path to file.
    """
    with resources.path("pyraingen.data", "coefficients.dat") as f:
        data_file_path = f
    return str(data_file_path)