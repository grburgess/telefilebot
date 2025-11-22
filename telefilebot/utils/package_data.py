from pathlib import Path
from importlib import resources


def get_path_of_data_dir() -> Path:
    """
    get the path of the package data directory

    :returns:

    """
    return resources.files("telefilebot") / "data"


def get_path_of_data_file(data_file: str) -> Path:
    """
    get the path of a dat file

    :param data_file: name of the data file
    :type data_file: str
    :returns:

    """
    file_path: Path = get_path_of_data_dir() / data_file

    return file_path


__all__ = [
    "get_path_of_data_file",
    "get_path_of_data_dir",
]
