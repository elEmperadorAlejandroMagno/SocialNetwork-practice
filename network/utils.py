from .models import Post, User, Follow, Notification, Like, Comment
from django.core.exceptions import PermissionDenied

CONTENT_TYPE = {
    'post': Post,
    'comment': Comment,
}

def check_permission(user_action, user_authorized):
    if user_action != user_authorized:
        raise PermissionDenied("You are not authorized to perform this action.")

def create_new_post(user: User, content: str) -> Post:
    post: Post = Post.objects.create(author=user, content=content)
    post.save()
    return post

def update_post(post_id: int, new_content: str) -> Post:
    try:
        post: Post = Post.objects.get(id=post_id)
        check_permission(post.author, post.author)
        post.content = new_content
        post.save()
        return post
    except Post.DoesNotExist:
        raise ValueError("Post not found")
    
def del_post(user, post_id: int) -> None:
    post_to_delete = Post.objects.get(id=post_id)
    check_permission(user, post_to_delete.author)
    post_to_delete.delete()

def toggle_like(user, content_type, object_id) -> tuple[int, str]:
    action: str | None = None
    if Like.objects.filter(user=user, content_type=CONTENT_TYPE[content_type], object_id=object_id).exists():
        like = Like.objects.get(user=user, content_type=CONTENT_TYPE[content_type], object_id=object_id)
        like.delete()
        action = "unliked"
    else:
        like = Like.objects.create(user=user, content_type=CONTENT_TYPE[content_type], object_id=object_id)
        like.save()
        if content_type == 'post':
            post = Post.objects.get(id=object_id)
            Notification.objects.create(
                sender=user,
                receiver=post.author,
                notification_type='like',
                post=post
            )
        elif content_type == 'comment':
            comment = Comment.objects.get(id=object_id).post
            Notification.objects.create(
                sender=user,
                receiver=comment.author,
                notification_type='like',
                comment=comment,
            )
        action = "liked"
    count = Like.objects.filter(content_type=content_type, object_id=object_id).count()
    return count, action

def toggle_follow(follower: User, username_to_follow: str) -> tuple[int, str]:
    user_to_follow: User = User.objects.get(username=username_to_follow)

    follow, created = Follow.objects.get_or_create(follower=follower, following=user_to_follow)
    if not created:
        # Si el follow ya existía, lo eliminamos (unfollow)
        follow.delete()
        action: str = "unfollowed"
        Notification.objects.get(sender=follower, receiver=user_to_follow, notification_type='follow').delete()
    else:
        action: str = "followed"
        Notification.objects.create(
            sender=follower,
            receiver=user_to_follow,
            notification_type='follow'
        )

    followers_count: int = user_to_follow.followers_count()
    return followers_count, action

def post_comment(user: User, post_id: int, content: str) -> bool:
    post: Post = Post.objects.get(id=post_id)
    comment: Comment = Comment.objects.create(author=user, post=post, content=content)
    comment.save()
    return True

def del_comment(user: User, comment_id: int) -> None:
    comment: Comment = Comment.objects.get(pk=comment_id)
    check_permission(user, comment.author)
    comment.delete()