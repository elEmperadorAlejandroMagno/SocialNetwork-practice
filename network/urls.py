
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("profile/<str:username>", views.profile, name="profile"),
    path("new_post", views.new_post, name="new_post"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("like", views.like_unlike, name="like_post"),
    path("follow", views.follow_unfollow, name="follow_unfollow"),
]
