from .models import Post, User, Follow, Notification, Like, Comment
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.utils.formats import date_format

CONTENT_TYPE = { 
    "post": ContentType.objects.get_for_model(Post), 
    "comment": ContentType.objects.get_for_model(Comment), 
}

NOTIFICATION_MESSAGES = {
    "like_post": "liked your post",
    "like_comment": "liked your comment",
    "follow": "started following you",
    "comment": "commented on your post"
}

def check_permission(user_action: User, user_authorized: User):
    if user_action != user_authorized:
        raise PermissionDenied("You are not authorized to perform this action.")

def likes_count(model, id):
    return Like.likes_count(CONTENT_TYPE[model], id)

def load_like_state(model_data, user):
    model_like_state_loaded = model_data
    if user.is_authenticated:
        for data in model_like_state_loaded:
            data.liked_by_user = data.likes.filter(user=user).exists()
    return model_like_state_loaded

# def load_like_state_comment(model_data, user):
#     model_like_state_loaded = model_data
#     if user.is_authenticated:
#         model_like_state_loaded.liked_by_user = model_like_state_loaded.likes.filter(user=user).exists()
#     return model_like_state_loaded

# def format_created_at_attribute(data):
#     for post in data:
#         post["created_at"] = date_format(post["created_at"], format='N j, Y, P', use_l10n=True)
#     return data