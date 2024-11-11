from dataclasses import dataclass
import pandas as pd

@dataclass
class StrategyStats:
    """Class to hold Strategy Statistics. It only gets updated """
    name: str = ''
    rows: int = 0
    # Index will be a Datetime Index called 'Exit time'. Dataframe will have 'Profit' and 'Cum. net profit' columns
    daily_df: pd.DataFrame = pd.DataFrame