from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
import json
from .models import Review, College

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('analytics:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('analytics:login')

@login_required
def dashboard_view(request):
    main_college = College.objects.filter(is_main=True).first()

    # Line Chart — динамика отзывов по месяцам
    monthly = Review.objects.filter(college=main_college) \
        .annotate(month=TruncMonth('date')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')
    line_labels = [obj['month'].strftime('%m.%Y') for obj in monthly]
    line_data = [obj['count'] for obj in monthly]

    # Bar Chart — топ ключевых жалоб
    negative_reviews = Review.objects.filter(college=main_college, sentiment='negative').values_list('text', flat=True)
    keywords = {
        'Туалеты': ['туалет', 'вонь', 'запах', 'грязн'],
        'Отопление': ['холодно', 'отопление', 'холод'],
        'Преподаватели': ['преподаватель', 'учитель', 'педагог'],
        'Администрация': ['администрация', 'руководство', 'директор'],
        'Лифт': ['лифт', 'этаж'],
        'Столовая': ['столовая', 'еда', 'буфет', 'питание'],
        'Практика': ['практика', 'выкидывают', 'стройка'],
        'Оценки': ['оценк', 'занижают', 'балл'],
        'Здание': ['здание', 'аренд', 'собственн'],
        'Каникулы': ['каникул', 'выгорани'],
    }
    complaint_labels = []
    complaint_data = []
    for keyword, words in keywords.items():
        count = 0
        for text in negative_reviews:
            text_lower = text.lower()
            if any(w in text_lower for w in words):
                count += 1
        if count > 0:
            complaint_labels.append(keyword)
            complaint_data.append(count)
    sorted_pairs = sorted(zip(complaint_data, complaint_labels), reverse=True)
    complaint_data = [x[0] for x in sorted_pairs]
    complaint_labels = [x[1] for x in sorted_pairs]

    # Pie Chart — тональность отзывов
    sentiments = Review.objects.filter(college=main_college).values('sentiment').annotate(count=Count('id'))
    sentiment_map = {'positive': 0, 'neutral': 0, 'negative': 0}
    for s in sentiments:
        sentiment_map[s['sentiment']] = s['count']
    pie_data = [sentiment_map['positive'], sentiment_map['neutral'], sentiment_map['negative']]

    # Bar Chart — распределение по оценкам
    rating_data = []
    for i in range(1, 6):
        rating_data.append(Review.objects.filter(college=main_college, rating=i).count())

    # Рекомендации
    avg_rating = Review.objects.filter(college=main_college).aggregate(avg=Avg('rating'))['avg'] or 0
    negative_count = sentiment_map['negative']
    recommendations = []
    if avg_rating < 4:
        recommendations.append('⚠️ Средний рейтинг ниже 4 — необходимо улучшить качество обслуживания')
    if negative_count > 10:
        recommendations.append(f'⚠️ {negative_count} отрицательных отзывов — проанализируйте жалобы и устраните проблемы')
    if avg_rating >= 4:
        recommendations.append('✅ Хороший рейтинг — продолжайте поддерживать качество')
    recommendations.append('💬 Отвечайте на все отзывы в 2GIS в течение 24 часов')
    recommendations.append('📢 Попросите довольных студентов оставить отзыв на 2GIS')
    recommendations.append('🏫 Улучшите условия: туалеты, вентиляция, столовая — частые жалобы в отзывах')
    recommendations.append('📋 Проведите анкетирование студентов для выявления проблем внутри колледжа')

    context = {
        'main_college': main_college,
        'line_labels': json.dumps(line_labels),
        'line_data': json.dumps(line_data),
        'bar_labels': json.dumps(complaint_labels),
        'bar_data': json.dumps(complaint_data),
        'pie_data': json.dumps(pie_data),
        'rating_data': json.dumps(rating_data),
        'avg_rating': round(avg_rating, 2),
        'total_reviews': Review.objects.filter(college=main_college).count(),
        'positive_count': sentiment_map['positive'],
        'negative_count': negative_count,
        'recommendations': recommendations,
    }
    return render(request, 'dashboard.html', context)

@login_required
def review_list_view(request):
    reviews = Review.objects.all().order_by('-date')
    source_filter = request.GET.get('source')
    sentiment_filter = request.GET.get('sentiment')
    college_filter = request.GET.get('college_id')

    if source_filter:
        reviews = reviews.filter(source=source_filter)
    if sentiment_filter:
        reviews = reviews.filter(sentiment=sentiment_filter)
    if college_filter:
        reviews = reviews.filter(college_id=college_filter)

    paginator = Paginator(reviews, 20)
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    colleges = College.objects.all()
    context = {
        'reviews': reviews,
        'colleges': colleges,
    }
    return render(request, 'review_list.html', context)