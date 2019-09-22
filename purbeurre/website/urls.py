from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search", views.results, name="results"),
    path("signup", views.signup, name="signup"),
    path("product", views.product, name="product"),
    path("signin", views.signin, name="signin"),
    path("account", views.account, name="account"),
    path("logout", views.logoutv, name="logout"),
    path("save", views.save, name="save"),
    path("myproducts", views.myproducts, name="myproducts")
]