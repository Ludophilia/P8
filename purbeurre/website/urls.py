from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home") # Et si on retire ça ? Ben plus d'urlconf.
]