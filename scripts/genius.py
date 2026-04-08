import os
import json
import sqlite3
import requests
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from get_logger import get_logger

load_dotenv()

def cache_api(table: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, identifier, *args, **kwargs):
            month = datetime.now().strftime('%Y-%m')
            with sqlite3.connect(self.db_path) as con:
                cursor = con.execute(f'''
                    SELECT timestamp, response FROM {table} 
                    WHERE identifier = ? AND timestamp LIKE ?
                ''', (str(identifier), f'{month}%'))
                cached = cursor.fetchone()
            if cached:
                timestamp, response = cached[0], cached[1]
                self.logger.info(f'Использован кэш для {table} с идентификатором {identifier} за {timestamp}') 
                return json.loads(response)
            response = func(self, identifier, *args, **kwargs)
            with sqlite3.connect(self.db_path) as con:
                con.execute(f'''
                    INSERT INTO {table} (timestamp, identifier, response)
                    VALUES (?, ?, ?)
                ''', (datetime.now().isoformat(), str(identifier), response))
            return json.loads(response)
        return wrapper
    return decorator

class Genius:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.session = requests.Session()
        token = os.getenv('GENIUS_CLIENT_ACCESS_TOKEN')
        self.session.headers.update({'Authorization': f'Bearer {token}'})
        os.makedirs('../data', exist_ok=True)
        self.db_path = '../data/genius.db'
        self._create_tables()

    def _create_tables(self):
        tables = ['searches', 'songs', 'artists', 'artist_songs', 'referents']
        with sqlite3.connect(self.db_path) as con:
            for table in tables:
                con.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table} (
                        _id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        identifier TEXT NOT NULL,
                        response TEXT NOT NULL
                    )
                ''')

    @cache_api('searches')
    def search(self, query: str) -> str:
        self.logger.info(f'Отправлен поисковый запрос: {query}')
        response = self.session.get('https://api.genius.com/search', params={'q': query})
        response.raise_for_status()
        return response.text
       
    @cache_api('songs')
    def song(self, song_id: int) -> str:
        self.logger.info(f'Получение данных песни с ID {song_id}') 
        response = self.session.get(f'https://api.genius.com/songs/{song_id}')
        response.raise_for_status()
        return response.text
    
    @cache_api('artists')
    def artist(self, artist_id: int) -> str:
        self.logger.info(f'Получение данных артиста с ID {artist_id}')
        response = self.session.get(f'https://api.genius.com/artists/{artist_id}')
        response.raise_for_status()
        return response.text
    
    @cache_api('artist_songs')
    def artist_songs(self, artist_id: int) -> str:
        url = f'https://api.genius.com/artists/{artist_id}/songs'
        responses = []
        page = 1
        while page:
            self.logger.info(f'Получение песен артиста {artist_id}, страница {page}')
            response = self.session.get(url, params={'sort': 'popularity', 'per_page': 50, 'page': page})
            response.raise_for_status()
            data = response.json()
            responses.append(data)
            page = data['response'].get('next_page')
        return json.dumps(responses)
    
    @cache_api('referents')
    def referents(self, song_id: int) -> str:
        url = 'https://api.genius.com/referents'
        responses = []
        page = 1
        while page:
            self.logger.info(f'Получение референтов для песни {song_id}, страница {page}')
            response = self.session.get(url, params={'song_id': song_id, 'text_format': 'plain', 'per_page': 50, 'page': page})
            response.raise_for_status()
            data = response.json()
            if not data['response']['referents']:
                break
            responses.append(data)
            page += 1
        return json.dumps(responses)
