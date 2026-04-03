import logging
from loging_setuper import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

import os
import pandas as pd
from datetime import datetime

def save_data(df: pd.DataFrame, filebasename: str) -> None:
    data_dir = '../data/'
    if not os.path.exists(data_dir):
        logger.info(f'Создана папка {data_dir}')
        os.makedirs(data_dir)
    
    logger.info(f'Сохранение данных {filebasename}')
    save_date = datetime.now().date().strftime('%Y-%m-%d').replace('-', '_')
    filename = f'{filebasename}_{save_date}.csv'
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath)
    logger.info(f'Данные успешно сохранены в {filepath}')
