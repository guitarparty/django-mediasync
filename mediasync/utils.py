import datetime
import os
from mediasync.conf import msettings

def get_file_mtime(url, path):
    """
    Takes a path to a file and returns a timestamp for the last modified 
    time of the file.
    """
    path = os.path.join(msettings['STATIC_ROOT'], path)
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(os.path.abspath(path))).strftime('%S%M%H%d%m%y')
    except OSError:
        # If the file can't be found.
        return '0'