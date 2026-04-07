import inspect
from pathlib import Path
import pandas as pd


def save_data(df: pd.DataFrame) -> None:
    directory = Path(__file__).parent.parent / 'data'
    directory.mkdir(exist_ok=True)
    filename = Path(inspect.currentframe().f_back.f_code.co_filename).stem
    df.to_csv(str(directory / f'{filename}.csv'))
