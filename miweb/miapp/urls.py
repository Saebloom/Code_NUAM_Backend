from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('miapp/', views.miapp, name='miapp'),
    path('acercade/', views.acercade, name='acercade'),
]