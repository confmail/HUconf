from datetime import datetime, timedelta


def is_time_between(begin_time, end_time):
    # If check time is not given, default to current UTC time
    check_time = datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def is_time_different_in_mins(start_time, mins) -> bool:
    return start_time < datetime.utcnow() - timedelta(minutes=mins)
