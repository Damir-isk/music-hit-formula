import requests
import sqlite3
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import pandas as pd

DATABASE_PATH = '../cache/images.db'

def _create_table():
    with sqlite3.connect(DATABASE_PATH) as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS image_features (
                url TEXT PRIMARY KEY,
                light REAL,
                contrast REAL,
                saturation REAL,
                hue REAL,
                clarity REAL,
                mean_r REAL,
                mean_g REAL,
                mean_b REAL
            )
        ''')

def processing(url):
    with sqlite3.connect(DATABASE_PATH) as con:
        query = 'SELECT * FROM image_features WHERE url = ?'
        cached = pd.read_sql_query(query, con, params=(url,))
    
    if not cached.empty:
        return cached.iloc[0]
    
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert('RGB')
    array = np.array(image)
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(array, cv2.COLOR_RGB2HSV)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    light = np.mean(gray)
    contrast = gray.std()
    saturation = np.mean(hsv[:, :, 1])
    hue = np.mean(hsv[:, :, 0])
    clarity = laplacian.var()
    mean_r = np.mean(array[:, :, 0])
    mean_g = np.mean(array[:, :, 1])
    mean_b = np.mean(array[:, :, 2])
    
    with sqlite3.connect(DATABASE_PATH) as con:
        con.execute('''
            INSERT INTO image_features (url, light, contrast, saturation, hue, clarity, mean_r, mean_g, mean_b)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (url, light, contrast, saturation, hue, clarity, mean_r, mean_g, mean_b))
    
    return pd.Series({
        'light': light,
        'contrast': contrast,
        'saturation': saturation,
        'hue': hue,
        'clarity': clarity,
        'mean_r': mean_r,
        'mean_g': mean_g,
        'mean_b': mean_b
    })
