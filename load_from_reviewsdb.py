import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import sqlite3
import random
from analytics.models import College, Review
from datetime import datetime, timedelta

college = College.objects.filter(is_main=True).first()

db_path = 'reviews_project/reviews.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

reviews = conn.execute('SELECT * FROM reviews').fetchall()
print(f'Найдено отзывов: {len(reviews)}')

Review.objects.filter(college=college).delete()
print('Старые отзывы удалены')

def get_sentiment(rating):
    if rating >= 4:
        return 'positive'
    elif rating == 3:
        return 'neutral'
    else:
        return 'negative'

def random_date():
    start = datetime(2024, 1, 1)
    end = datetime(2026, 4, 29)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

saved = 0
for r in reviews:
    try:
        rating = int(r['rating']) if r['rating'] else 5
        text = r['text'] or ''
        author = r['author_name'] or 'Аноним'
        date = random_date()

        if text:
            Review.objects.create(
                college=college,
                source='2gis',
                rating=rating,
                text=text,
                author=author,
                date=date,
                sentiment=get_sentiment(rating),
            )
            saved += 1
    except Exception as e:
        print(f'Ошибка: {e}')

conn.close()
print(f'Сохранено: {saved} отзывов!')