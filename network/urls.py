
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("load-more", views.load_more, name="load-more"),
    path("user/<str:user>", views.user, name="user"),
    path("follow", views.follow, name="follow"),
    path("followPage", views.followPage, name="followPage"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("like/<int:post>", views.like, name="like")
]
