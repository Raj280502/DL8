# brain/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_brain_data),
    path('list/', views.list_brain_data),
]
