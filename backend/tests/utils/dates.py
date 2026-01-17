from datetime import datetime, date
from typing import Optional


def get_epoch_time_s():
    """ 
    Get unique string based on current epoch time
    """
    return datetime.now().timestamp()

def make_date(
    *,
    year: int,
    month: Optional[int] = 1,
    day: Optional[int] = 1,
) -> str:
    """
    Examples:
        make_date(year=2022)
        make_date(year=2022, month=6)
        make_date(year=2022, day=15)
    """
    return date(year, month or 1, day or 1).isoformat()