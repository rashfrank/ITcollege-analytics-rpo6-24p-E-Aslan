from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_view, name='dashboard'),
    path('reviews/', views.review_list_view, name='review_list'),
]