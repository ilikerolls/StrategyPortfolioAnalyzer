import csv
import os
import shutil

import pandas as pd

from src.conf_setup import DATA_IN_DIR, logger, DATA_IN_ARCH_DIR, DB_STRAT_DIR
from src.data.types.data_trades import DataTrades


class DataLoaderCSV:
    """Loads files from the data in directory"""

    def __init__(self):
        self.data_trades = DataTrades()
        # Load pre-existing Strategy Database Files into self.data_trades before reading any new .csv's
        self._load_strat_dbs()

    def load_strat_csvs(self) -> DataTrades:
        """
        Load data from .csv files
        :return: A DataTrades object filled with each Strategy's Trades
        """
        files_processed = 0
        in_files = os.listdir(DATA_IN_DIR)
        for file in in_files: # combine files into 1
            if os.path.splitext(file)[-1].lower() == ".csv":
                csv_file = os.path.join(DATA_IN_DIR, file)
                csv_file_arch = os.path.join(DATA_IN_ARCH_DIR, file)
                logger.debug(f"Processing file: {file}.")
                try:
                    row_counter = 0
                    with open(csv_file, 'r') as fh:
                        csv_reader = csv.DictReader(f=fh, fieldnames=DataTrades.strat_cols)
                        # csv_reader = csv.reader()
                        # Iterate over each row in the CSV file
                        for row in csv_reader:
                            # skip header
                            if row['Trade number'].lower() == 'trade number': continue
                            del row[None]
                            self.data_trades.add_trade_data(row=row)
                            row_counter += 1
                    files_processed += 1
                    logger.info(f"Attempted to Load {row_counter} Trades from {file}. Processed {files_processed} files. NOTE: There maybe duplicate Trades filtered out after this.")
                     # shutil.move(csv_file, csv_file_arch) # Remove file in future? os.remove(full_filename)
                except Exception as e:
                    logger.exception(f"Failed to load Trade file [{csv_file}] into database. Exception: {e}")
        if files_processed > 0:
            self.data_trades.dedupe()
            self.save_db()
        return self.data_trades

    def _load_strat_dbs(self):
        """
        Load Strategy Database files
        """
        strat_db_files = os.listdir(DB_STRAT_DIR)
        for strat_db in strat_db_files:
            if os.path.splitext(strat_db)[-1].lower() == ".parquet":
                strat_db_file = os.path.join(DB_STRAT_DIR, strat_db)
                self.data_trades.add_db_strat_trades(trades_df=pd.read_parquet(path=strat_db_file))
                logger.info(f"Loaded Strategy Database file: {strat_db_file}")

    def save_db(self, strat_name: str = None):
        """
        Save a Strategies Database to a database file
        :param strat_name: String representing the name of the strategy
        """
        if strat_name is None:
            for name, strat_df in self.data_trades.trade_data.items():
                strat_df = self.data_trades.get_strat_df(name)
                strat_db_file = os.path.join(DB_STRAT_DIR, f"{name}.parquet")
                logger.debug(f"{name}: Saving [{len(strat_df)}] Rows/Trades to [{strat_db_file}]")
                strat_df.to_parquet(path=strat_db_file)
        else:
            strat_db_file = os.path.join(DB_STRAT_DIR, f"{strat_name}.parquet")
            strat_df = self.data_trades.get_strat_df(strat_name)
            strat_df.to_parquet(path=strat_db_file)

