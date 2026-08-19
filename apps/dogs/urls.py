from django.urls import path
from . import views

app_name = 'dogs'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('dogs/<slug:slug>/', views.dog_detail, name='detail'),
]
