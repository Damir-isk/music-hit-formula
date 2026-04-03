import logging
from loging_setuper import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

import requests
from bs4 import BeautifulSoup
import pandas as pd

from data_saver import save_data

def fetch_html(url: str) -> str:
    logger.info(f'Отправлен запрос к сайту {url}')
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f'Получена разметка сайта {url}')
        return response.text
    logger.error(f'Получена ошибка {response.status_code} при обращении к сайту {url}')
    logger.debug(f'Текст ошибки: {response.text}')
    response.raise_for_status()

def parse_html(html: str) -> list:
    logger.info('Начался процесс извлечения данных из разметки сайта')
    soup = BeautifulSoup(html, 'html.parser')
    table_rows = soup.find_all('tr')
    if not table_rows:
        logger.error('Таблица не найдена на странице')
        logger.debug(f'Содержимое страницы: {soup}')
        raise ValueError()
    if len(table_rows) == 1:
        logger.error(f'Таблица пуста, есть только заголовки')
        logger.debug(f'Заголоки таблицы: {table_rows[0]}')
        raise ValueError()
    body_rows = table_rows[1:]
    logger.info(f'Получено {len(body_rows)} строк таблицы')
    parsed_data = []
    for i, row in enumerate(body_rows, start=1):
        cells = row.find_all('td')
        if len(cells) != 7:
            logger.error(f'В строке {i} получено {len(cells)} ячеек, ожидалось 7')
            logger.debug(f'Содержимое строки: {row}')
            raise IndexError()
        artist_and_track, *stats = cells
        links = artist_and_track.find_all('a')
        if len(links) != 2:
            logger.warning(f'В строке {i} надено {len(links)} ссылок, ожидалось 2')
            logger.debug(f'Содержимое ячейки: {artist_and_track}')
            continue
        artist_name, track_title = [x.text.strip() for x in links]
        parsed_data.append([i, artist_name, track_title] + [x.text.strip() for x in stats])
    logger.info(f'Успешно извлечено {100 * len(parsed_data) / len(body_rows):.2f}% строк')
    return parsed_data

def clean_data(raw_data: list) -> pd.DataFrame:
    logger.info('Начался процесс очистки данных')
    columns = ['rank', 'artist_name', 'track_title', 'days_on_chart', 'top_10_days', 'peak_position', 'peak_occurrence', 'peak_streams', 'total_streams']
    df = pd.DataFrame(raw_data, columns=columns).set_index('rank')
    df['artist_name'] = df['artist_name'].str.encode('utf-8').str.decode('latin-1')
    df['track_title'] = df['track_title'].str.encode('utf-8').str.decode('latin-1')
    df['days_on_chart'] = df['days_on_chart'].replace('', None).astype('Int64')
    df['top_10_days'] = df['top_10_days'].replace('', None).astype('Int64')
    df['peak_position'] = df['peak_position'].replace('', None).astype('Int64')
    df['peak_occurrence'] = df['peak_occurrence'].str.extract(r'\(x(\d+)\)').replace('', None).astype('Int64')
    df['peak_streams'] = df['peak_streams'].str.replace(',', '').replace('', None).astype('Int64')
    df['total_streams'] = df['total_streams'].str.replace(',', '').replace('', None).astype('Int64')
    logger.info('Данные очищены')
    return df

def main():
    url = 'https://kworb.net/spotify/country/global_daily_totals.html'
    try:
        html = fetch_html(url)
        raw_data = parse_html(html)
        df = clean_data(raw_data)
        save_data(df, 'kworb_global_daily_totals')
        logger.info('Выгрузка данных с kworb_global_daily_totals прошла успешно')
    except Exception as e:
        logger.critical(e, exc_info=True)


if __name__ == '__main__':
    main()
