import datetime
import os


def get_file_modification_time(path: str) -> datetime.datetime:
    timestamp: float = os.path.getmtime(path)
    time = datetime.datetime.fromtimestamp(timestamp)
    return time


def set_file_modification_time(path: str, mod_time: datetime.datetime) -> None:
    assert os.path.isfile(path), path

    # Convert datetime to a timestamp
    timestamp = mod_time.timestamp()
    # Set the modification time (and optionally access time)
    os.utime(path, times=(timestamp, timestamp))
