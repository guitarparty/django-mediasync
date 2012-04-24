import datetime
import os

def get_file_mtime(url, path):
    """
    Takes a path to a file and returns a timestamp for the last modified 
    time of the file.
    """

    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(os.path.abspath(path))).strftime('%S%M%H%d%m%y')
    except OSError:
        # If the file can't be found.
        return '0'