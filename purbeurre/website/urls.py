from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('search', views.results, name="results"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin")
]