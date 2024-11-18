from datetime import date
import pandas as pd

from src.conf_setup import LIVE_SETTINGS_FILE, logger
from src.utils import get_dt_from_str

class LiveSettings:
    """Persistent Settings for Live Dashboard"""

    COLUMNS: list = ['LIVE_DATE', 'STOP_LOSS']

    def __init__(self):
        self.live_settings = None
        self.live_strategies: list = []
        self._load_settings()

    def _load_settings(self):
        """ Load Previous Live Settings from db file """
        try:
            self.live_settings = pd.read_parquet(path=LIVE_SETTINGS_FILE)
            self.live_strategies = self.live_settings.index
        except FileNotFoundError:
            self.live_settings = pd.DataFrame()
            self.live_strategies = []

    def get_strat_date(self, name: str) -> date | None:
        """
        Get Start Live Date for Strategy name
        :param name: Name of the Strategy
        :return: A date Object Representing the Strategy Start Date. Or None if we couldn't locate the Strategy in our DB
        """
        try:
            str_date = self.live_settings.loc[name]['LIVE_DATE']
            dt_obj = get_dt_from_str(str_date)
            return dt_obj.date()
        except KeyError:
            return None

    def get_strat_sl(self, name: str) -> float | None:
        """
        Return Strategy's Stop Loss
        :param name: The name of the Strategy
        :return: A float representing the Stop Loss. Or None if the Strategy isn't available in the database
        """
        try:
            strat_stop_loss = self.live_settings.loc[name]['STOP_LOSS']
            return float(strat_stop_loss)
        except KeyError:
            return None


    def save_settings(self, settings: dict):
        """
        Save LiveSettings to a database
        :param settings: A Dictionary representing the Settings to be saved
        """
        self.live_settings = pd.DataFrame.from_dict(data=settings, orient='index', columns=LiveSettings.COLUMNS)
        self.live_settings.to_parquet(path=LIVE_SETTINGS_FILE)
        self.live_strategies = self.live_settings.index
        logger.debug(f"Saved Live Settings\n{self.live_settings}")