from utils import dates

def get_unique_epoch_s():
    return str(dates.get_epoch_time_s())

def get_unique_s():
    return get_unique_epoch_s()

def create_field(field):
    return f"{field}-{get_unique_s()}"