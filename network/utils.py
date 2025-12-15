from .models import Post, User, Follow, Notification


def create_new_post(user: User, content: str) -> Post:
    post: Post = Post.objects.create(author=user, content=content)
    post.save()
    return post

def update_post(post_id: int, new_content: str) -> Post:
    try:
        post: Post = Post.objects.get(id=post_id)
        post.content = new_content
        post.save()
        return post
    except Post.DoesNotExist:
        raise ValueError("Post not found")

def toggle_like(user: User, post_id: int) -> tuple[int, str]:
    try:
        post: Post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        raise ValueError("Post not found")

    like, created = post.likes.get_or_create(user=user)
    if not created:
        # Si el like ya existía, lo eliminamos (unlike)
        like.delete()
        action: str = "unliked"
        Notification.object.get(sender=user, receiver=post.author, post=post, notification_type='like').delete()
    else:
        action: str = "liked"
        Notification.objects.create(
            sender=user,
            receiver=post.author,
            notification_type='like',
            post=post
        )

    likes_count: int = post.likes_count()
    return likes_count, action

def toggle_follow(follower: User, username_to_follow: str) -> tuple[int, bool]:
    user_to_follow: User = User.objects.get(username=username_to_follow)

    follow, created = Follow.objects.get_or_create(follower=follower, following=user_to_follow)
    if not created:
        # Si el follow ya existía, lo eliminamos (unfollow)
        follow.delete()
        action: str = "unfollowed"
        Notification.object.get(sender=follower, receiver=user_to_follow, notification_type='follow').delete()
    else:
        action: str = "followed"
        Notification.objects.create(
            sender=follower,
            receiver=user_to_follow,
            notification_type='follow'
        )

    followers_count: int = user_to_follow.followers_count()
    return followers_count, action