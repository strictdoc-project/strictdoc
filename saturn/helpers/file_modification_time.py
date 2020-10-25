import datetime
import os


def get_file_modification_time(path):
    timestamp = (os.path.getmtime(path))
    time = datetime.datetime.fromtimestamp(timestamp)
    return time
