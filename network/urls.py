
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("posts", views.get_posts, name="get_posts"),
    path("post/<int:post_id>", views.post_details, name="post_details"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    path("profile/<str:username>", views.profile, name="profile"),
    path("post/new_post", views.new_post, name="new_post"),
    path("post/edit", views.edit_post, name="edit_post"),
    path("post/delete", views.delete_post, name="delete_post"),
    path("post/like", views.like_unlike_in_post, name="like_post"),
    path("post/new_comment", views.create_comment, name="new_comment"),
    path("post/comment/like", views.like_unlike_in_comment, name="like_comment"),
    path("post/comment/delete", views.delete_comment, name="delete_comment"),
    path("follow", views.follow_unfollow, name="follow_unfollow"),
    path("notifications/mark_as_read", views.mark_notifications_as_read, name="mark_notifications_as_read"),
]
