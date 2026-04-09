import os
import sqlite3
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from get_logger import get_logger

class Kworb:
    SCHEMA = [
        ('date', 'TEXT'),
        ('rank', 'INTEGER'),
        ('artist_name', 'TEXT'),
        ('track_title', 'TEXT'),
        ('days_on_chart', 'INTEGER'),
        ('top_10_days', 'INTEGER'),
        ('peak_position', 'INTEGER'),
        ('peak_occurrence', 'INTEGER'),
        ('peak_streams', 'INTEGER'),
        ('total_streams', 'INTEGER'),
    ]

    def __init__(self):
        self.logger = get_logger(__name__)
        os.makedirs('../cache', exist_ok=True)
        self.db_path = '../cache/kworb.db'
        self._create_table()

    def _create_table(self):
        columns_query = ', '.join([f'"{name}" {dtype}' for name, dtype in self.SCHEMA])
        with sqlite3.connect(self.db_path) as con:
            con.execute(f'CREATE TABLE IF NOT EXISTS spotify_daily_totals ({columns_query})')
            con.execute('CREATE INDEX IF NOT EXISTS idx_date ON spotify_daily_totals (date)')

    def spotify_daily_chart_totals(self, date: str) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as con:
            query = 'SELECT * FROM spotify_daily_totals WHERE date = ?'
            cached = pd.read_sql_query(query, con, params=(date,))
        if not cached.empty:
            self.logger.info(f'Данные за {date} число получены из кэша')
            return cached.set_index('rank')
        now = datetime.now().strftime('%Y-%m-%d')
        self.logger.info(f'Данных за {date} нет. Берем данные за {now}...')
        with sqlite3.connect(self.db_path) as con:
            query = 'SELECT * FROM spotify_daily_totals WHERE date = ?'
            cached = pd.read_sql_query(query, con, params=(now,))
        if not cached.empty:
            self.logger.info(f'Данные за {now} число получены из кэша')
            return cached.set_index('rank')
        response = requests.get('https://kworb.net/spotify/country/global_daily_totals.html')
        response.raise_for_status()
        response.encoding = 'utf-8'
        self.logger.info(f'Данные успешно получены')
        soup = BeautifulSoup(response.text, 'html.parser')
        body_rows = soup.find_all('tr')[1:]
        parsed_data = []
        for i, row in enumerate(body_rows, start=1):
            cells = row.find_all('td')
            if len(cells) != 7:
                continue
            links = cells[0].find_all('a')
            if len(links) != 2:
                continue
            artist_name, track_title = [x.text.strip() for x in links]
            parsed_data.append([now, i, artist_name, track_title] + [x.text.strip() for x in cells[1:]])
        self.logger.info('Очистка данных...')
        df = pd.DataFrame(parsed_data, columns=list(dict(self.SCHEMA).keys())) 
        df['artist_name'] = df['artist_name'].str.strip()
        df['track_title'] = df['track_title'].str.strip()
        df['top_10_days'] = df['top_10_days'].replace('', 0).astype(int)
        df['peak_occurrence'] = df['peak_occurrence'].str.extract(r'\(x(\d+)\)').fillna(1).astype(int)
        df['peak_streams'] = df['peak_streams'].str.replace(',', '').astype(int)
        df['total_streams'] = df['total_streams'].str.replace(',', '').astype(int)
        self.logger.info('Сохранение данных...')
        with sqlite3.connect(self.db_path) as con:
            df.to_sql('spotify_daily_totals', con, if_exists='append', index=False)
        self.logger.info(f'Данные за {now} успешно сохранены')
        return df.set_index('rank')
