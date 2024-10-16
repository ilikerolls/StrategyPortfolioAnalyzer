import os
import quantstats as qs
import shutil

import pandas as pd

from src.conf_setup import DATA_IN_DIR, logger, DATA_IN_ARCH_DIR
from src.utils import accounting_to_num, to_datetime


class DataloaderCSV:
    """Loads files from the data in directory"""

    # Dictionary of Trade Data with trade_data['Strategy_Name'] = Pandas Dataframe of Trades
    trade_data: dict[str, pd.DataFrame] = {}
    # Data Converters
    data_converters = {'Profit': accounting_to_num,'Cum. net profit': accounting_to_num,
                         "Commission": accounting_to_num,'ETD': accounting_to_num, 'MAE': accounting_to_num,'MFE': accounting_to_num, 'Entry time': to_datetime, 'Exit time': to_datetime}

    def __init__(self, in_dir: str = None):
        """
        :param in_dir: Optional: Default loads directory in constants. Otherwise give a directory name to check for
        .csv files
        """
        self.in_dir = DATA_IN_DIR if in_dir is None else in_dir

    def load_data(self):
        """
        Load data from .csv files
        """
        in_files = os.listdir(self.in_dir)
        for file in in_files: # combine files into 1
            if os.path.splitext(file)[-1].lower() == ".csv":
                full_filename = os.path.join(self.in_dir, file)
                arch_filename = os.path.join(DATA_IN_ARCH_DIR, file)
                try:
                    # Set header to 1st row and Index to Strategy Name
                    strat_df = pd.read_csv(full_filename, header=0, index_col=None, converters=self.data_converters)
                    strategy_name = strat_df['Strategy'].iloc[0]
                    self.trade_data[strategy_name] = strat_df
                    logger.info(f"Loaded Strategy [{strategy_name}] with [{len(strat_df) - 1}] Trades from {full_filename}. Removing file now that it has already been processed.")
                    #os.remove(full_filename)
                    shutil.move(full_filename, arch_filename)
                    print(strat_df.columns)
                    print(f"Data Column Types: {strat_df.dtypes}")
                    print(f"Indexes: {strat_df.index.dtype}")
                except Exception:
                    logger.exception(f"Failed to load Trade file [{full_filename}] into database.")

