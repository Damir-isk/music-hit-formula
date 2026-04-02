import requests
import pandas as pd
from bs4 import BeautifulSoup

def main():
    # Выгрузка данных с сайта ⛏️
    url = 'https://kworb.net/spotify/country/global_daily_totals.html'
    response = requests.get(url=url)
    assert response.status_code == 200
    soup = BeautifulSoup(markup=response.text, features='html.parser')
    header, *rows = soup.find_all('tr')

    # Формирование таблицы 🍽️ (на слово table предлагается ещё ракетка для настольного тениса, но пустая тарелка мне нравиться больше)
    columns = ['rank', 'artist_name', 'track_title', 'days_on_chart', 'top_10_days', 'peak_position', 'peak_occurrence', 'peak_streams', 'total_streams']
    data = []
    for i, row in enumerate(rows, start=1):
        artist_and_track, *stats = row.find_all('td')
        artist_name, track_title = [x.text for x in artist_and_track.find_all('a')]
        data.append([i, artist_name, track_title] + [x.text for x in stats])
    df = pd.DataFrame(data=data, columns=columns)
    df = df.set_index('rank')

    # Приведение типов 🧹
    df['days_on_chart'] = df['days_on_chart'].replace('', None).astype('Int64')
    df['top_10_days'] = df['top_10_days'].replace('', None).astype('Int64')
    df['peak_position'] = df['peak_position'].replace('', None).astype('Int64')
    df['peak_occurrence'] = df['peak_occurrence'].str.extract(r'\(x(\d+)\)').replace('', None).astype('Int64')
    df['peak_streams'] = df['peak_streams'].str.replace(',', '').replace('', None).astype('Int64')
    df['total_streams'] = df['total_streams'].str.replace(',', '').replace('', None).astype('Int64')

    df.to_csv(f'../data/kworb_global_daily_totals.csv')


if __name__ == '__main__':
    main()
