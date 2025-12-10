
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("profile/<str:username>", views.profile, name="profile"),
    path("post/new_post", views.new_post, name="new_post"),
    path("post/edit", views.edit_post, name="edit_post"),
    path("post/delete", views.delete_post, name="delete_post"),
    path("post/like", views.like_unlike, name="like_post"),
    path("follow", views.follow_unfollow, name="follow_unfollow"),
]
