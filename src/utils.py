from datetime import datetime, date

def accounting_to_num(value) -> float:
    """Converts an accounting number string to a float."""
    value = value.replace('$', '').replace('(', '-').replace(')', '').replace(',', '')
    return float(value)

def get_cur_date() -> date:
    """:return: Current Date in a format that DatePicker understands"""
    current_time: datetime = datetime.now()
    return date(current_time.year, current_time.month, current_time.day)

def get_dt_from_str(dt_string: str, date_format='%Y-%m-%d') -> datetime:
    """
    Get datetime object from a string
    :param dt_string: String to convert to datetime object Ex: 2024-01-01
    :param date_format: The format to translate the dt_string from
    :return: Date time object
    """
    return datetime.strptime(dt_string.replace('T00:00:00', ''), date_format)

def to_datetime(value) -> datetime:
    """Converts String into a datetime object usable in Pandas"""
    date_format = '%m/%d/%Y %H:%M:%S %p'
    return datetime.strptime(value, date_format)


from threading import Lock

class Singleton(type):
    """
    Create a thread safe Singleton Class. Just add metaclass=metaclass=Singleton to your Class
    ex:

    from lib import Singleton
    class KlineHistory(metaclass=Singleton):
        def __init__(self):
            print("I am not a Singleton Class & will give the same instance even when called from Threads")
    """
    _instances = {}
    __singleton_lock = Lock()

    def __call__(cls, *args, **kwargs):
        # Check again for instance just in case another thread beat us to it
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]