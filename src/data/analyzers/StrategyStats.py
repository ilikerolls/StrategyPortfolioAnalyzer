from dataclasses import dataclass
import pandas as pd

@dataclass
class StrategyStats:
    """Class to hold Strategy Statistics. It only gets updated """
    name: str = ''
    rows: int = 0
    daily_df: pd.DataFrame = pd.DataFrame