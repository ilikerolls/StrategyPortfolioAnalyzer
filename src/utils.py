from datetime import datetime


def accounting_to_num(value) -> float:
    """Converts an accounting number string to a float."""
    value = value.replace('$', '').replace('(', '-').replace(')', '').replace(',', '')
    return float(value)


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
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]