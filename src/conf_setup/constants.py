# Top/Parent directory to the Bot
import os
from pathlib import Path
APP_NAME = 'StrategyPorfolioAnalyzer'
# Root directory of the Program
ROOT_DIR: str = str(Path(__file__).parent.parent.parent)
# Directory to Hold .csv files to process
DATA_DIR = os.path.join(ROOT_DIR, "data")
DATA_IN_DIR = os.path.join(DATA_DIR, "in")
DATA_IN_ARCH_DIR = os.path.join(DATA_IN_DIR, "arch")

# Logging
LOG_FILE = os.path.join(ROOT_DIR, "logs", f"{APP_NAME}.log")
LOG_FILE_ERR = os.path.join(ROOT_DIR, "logs", f"{APP_NAME}.log")
LOG_LEVEL = 'DEBUG'
LOG_BACKUPS = 2

# Database Settings
DB_DIR = os.path.join(DATA_DIR, "dbs")
DB_STRAT_DIR = os.path.join(DB_DIR, "strategies")