from get_logger import get_logger
from save_data import save_data
import requests
from bs4 import BeautifulSoup
import pandas as pd


logger = get_logger(__name__)


logger.info(f'Отправляю запрос ...')
url = 'https://kworb.net/spotify/country/global_daily_totals.html'
response = requests.get(url)
if response.status_code != 200:
    logger.error(f'Код ошибки: {response.status_code}')
    logger.debug(f'Текст ошибки: {response.text}')
    response.raise_for_status()
logger.info(f'Ответ получен успешно')
response.encoding = 'utf-8'
html = response.text


logger.info('Извлекаю разметку ...')
soup = BeautifulSoup(html, 'html.parser')
table_rows = soup.find_all('tr')
if not table_rows:
    logger.error('Таблица не найдена')
    logger.debug(f'Содержимое страницы: {soup}')
    raise ValueError()
if len(table_rows) == 1:
    logger.error(f'Таблица пуста')
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


logger.info('Чищую данные ...')
columns = ['rank', 'artist_name', 'track_title', 'days_on_chart', 'top_10_days', 'peak_position', 'peak_occurrence', 'peak_streams', 'total_streams']
df = pd.DataFrame(parsed_data, columns=columns).set_index('rank')
df['days_on_chart'] = df['days_on_chart'].replace('', None).astype('Int64')
df['top_10_days'] = df['top_10_days'].replace('', None).astype('Int64')
df['peak_position'] = df['peak_position'].replace('', None).astype('Int64')
df['peak_occurrence'] = df['peak_occurrence'].str.extract(r'\(x(\d+)\)').replace('', None).astype('Int64')
df['peak_streams'] = df['peak_streams'].str.replace(',', '').replace('', None).astype('Int64')
df['total_streams'] = df['total_streams'].str.replace(',', '').replace('', None).astype('Int64')
logger.info('Данные очищены')


logger.info('Сохраняю данные ...')
save_data(df)
logger.info('Данные сохранены')
