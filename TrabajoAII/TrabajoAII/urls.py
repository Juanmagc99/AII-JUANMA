from django.contrib import admin
from django.urls import path
from principal import views

urlpatterns = [
    path('', views.inicio),
    path('populate/', views.populate),
    path('listJobs/', views.listJobs),
    path('searchByMultipleField/', views.searchByMultipleField),
    path('searchBySkills/', views.searchBySkills),
    path('createDict/', views.create_dic),
    path('similarJob/', views.recommendedJob)
]
