from django.contrib import admin
from django.urls import path
from principal import views

urlpatterns = [
    path('', views.inicio),
    path('populate/', views.populate),
    path('whooshLoad/', views.whooshLoad),
    path('searchJobTitle/', views.searchByTitle)

]
