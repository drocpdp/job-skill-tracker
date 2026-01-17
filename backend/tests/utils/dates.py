from datetime import datetime


def get_epoch_time_s():
    """ 
    Get unique string based on current epoch time
    """
    return datetime.now().timestamp()