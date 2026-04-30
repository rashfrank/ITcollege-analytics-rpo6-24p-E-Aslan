from django.db import models

class College(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    is_main = models.BooleanField(default=False, verbose_name='Наш колледж')

    def __str__(self):
        return self.name

class Review(models.Model):
    SOURCE_CHOICES = [
        ('2gis', '2GIS'),
        ('google', 'Google'),
    ]
    SENTIMENT_CHOICES = [
        ('positive', 'Положительный'),
        ('neutral', 'Нейтральный'),
        ('negative', 'Отрицательный'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, verbose_name='Колледж')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, verbose_name='Источник')
    rating = models.IntegerField(verbose_name='Оценка (1-5)')
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.CharField(max_length=255, verbose_name='Автор')
    date = models.DateTimeField(verbose_name='Дата')
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, verbose_name='Тональность')

    def __str__(self):
        return f"{self.college.name} — {self.rating}★ ({self.source})"

class InstagramPost(models.Model):
    POST_TYPE_CHOICES = [
        ('photo', 'Фото'),
        ('video', 'Видео'),
        ('reels', 'Reels'),
        ('story', 'Story'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, verbose_name='Колледж')
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, verbose_name='Тип')
    likes = models.IntegerField(default=0, verbose_name='Лайки')
    comments = models.IntegerField(default=0, verbose_name='Комментарии')
    reach = models.IntegerField(default=0, verbose_name='Охват')
    date = models.DateTimeField(verbose_name='Дата публикации')
    caption = models.TextField(blank=True, verbose_name='Подпись')

    def __str__(self):
        return f"{self.college.name} — {self.post_type} ({self.date.strftime('%d.%m.%Y')})"