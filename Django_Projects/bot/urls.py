from django.contrib import admin
from django.urls import path
from .views import training, query, home

urlpatterns = [
    path('', home, name='home view'),
    path('training/', training, name='Training view'),
    path('query/', query, name='Query view')
]
