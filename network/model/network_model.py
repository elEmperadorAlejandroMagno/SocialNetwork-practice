from dataclasses import dataclass
from ..models import Post, User, Follow, Notification, Like, Comment
from ..utils import check_permission, CONTENT_TYPE, likes_count, load_like_state, NOTIFICATION_MESSAGES
from django.db.models.query import QuerySet

@dataclass
class NotificationData:
    sender: User
    receiver: User
    notification_type: str
    content: Post | Comment | None = None
    


class NetworkModel:

    @staticmethod
    def create_notification(data: NotificationData) -> Notification | None:
        if data.receiver == data.sender:
            return None

        if data.notification_type == 'like_post':
                notification = Notification.objects.create(
                    sender=data.sender,
                    receiver=data.receiver,
                    notification_type=data.notification_type,
                    post=data.content,
                    message=f"{data.sender.username}, {NOTIFICATION_MESSAGES[data.notification_type]}"
                )

        elif data.notification_type == 'like_comment':
                notification = Notification.objects.create(
                    sender=data.sender,
                    receiver=data.receiver,
                    notification_type= data.notification_type,
                    comment=data.content,
                    message=f"{data.sender.username}, {NOTIFICATION_MESSAGES[data.notification_type]}"
                )
        elif data.notification_type == 'follow':
                notification = Notification.objects.create(
                    sender=data.sender,
                    receiver=data.receiver,
                    notification_type=data.notification_type,
                    message=f"{data.sender.username}, {NOTIFICATION_MESSAGES[data.notification_type]}"
                )

        elif data.notification_type == 'comment':
            notification = Notification.objects.create(
                sender=data.sender,
                receiver=data.receiver,
                notification_type=data.notification_type,
                comment=data.content,
                message=f"{data.sender.username}, {NOTIFICATION_MESSAGES[data.notification_type]}"
            )
        notification.save()
        return notification

    @staticmethod
    def get_all_posts(user: User, filter: str|None = None) -> QuerySet[Post]:
        posts = None
        if filter == "following":
            posts = NetworkModel.get_all_following_posts(user)
        else:
            posts = Post.objects.all().order_by("-created_at")[:10]
        return load_like_state(posts, user)
    
    @staticmethod
    def get_all_following_posts(user: User) -> QuerySet[Post]:
        following_users = [follow.following for follow in Follow.objects.filter(follower=user)]
        posts = Post.objects.filter(author__in=following_users).order_by("-created_at")
        return load_like_state(posts, user)
    
    @staticmethod
    def get_slice_posts(user: User, starts: int, ends: int) -> QuerySet[Post]:
        posts = Post.objects.all().order_by("-created_at")[starts:ends]
        return load_like_state(posts, user)
    
    @staticmethod
    def get_user_posts(user: User) -> QuerySet[Post]:
        posts = Post.objects.filter(author=user).order_by("-created_at")
        return load_like_state(posts, user)
    

    @staticmethod
    def get_post_by_id(user: User, post_id: int) -> tuple[Post, list]:
        post = Post.objects.get(pk=post_id)
        comments = post.comments.all().order_by("-created_at") #type: ignore
        comments = load_like_state(comments, user)
        post = load_like_state([post], user)
        return post[0], comments
    
    @staticmethod
    def create_new_post(user: User, content: str) -> Post:
        post: Post = Post.objects.create(author=user, content=content)
        post.save()
        return post

    @staticmethod
    def update_post(post_id: int, new_content: str) -> Post:
        try:
            post: Post = Post.objects.get(id=post_id)
            check_permission(post.author, post.author)
            post.content = new_content
            post.save()
            return post
        except Post.DoesNotExist:
            raise ValueError("Post not found")

    @staticmethod        
    def del_post(user: User, post_id: int) -> None:
        post_to_delete = Post.objects.get(id=post_id)
        check_permission(user, post_to_delete.author)
        post_to_delete.delete()

    @staticmethod
    def toggle_like(user: User, content_type: str, object_id: int) -> tuple[int, str]:
        action: str | None = None

        if Like.objects.filter(user=user, content_type=CONTENT_TYPE[content_type], object_id=object_id).exists():
            like = Like.objects.get(user=user, content_type=CONTENT_TYPE[content_type], object_id=object_id)
            like.delete()
            action = "unliked"
        else:
            like = Like.objects.create(user=user, content_type=CONTENT_TYPE[content_type], object_id=object_id)
            like.save()
            notification = NetworkModel.create_notification(data = NotificationData(
                sender= user,
                receiver= like.content_object.author, #type:ignore
                notification_type= f"like_{content_type}",
                content= like.content_object
            ))
            action = "liked"
        count = Like.likes_count(CONTENT_TYPE[content_type], object_id)
        return count, action

    @staticmethod
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
            notification = NetworkModel.create_notification(data = NotificationData(
                sender= follower,
                receiver= user_to_follow,
                notification_type= "follow",
            ))

        followers_count: int = user_to_follow.followers_count()
        return followers_count, action

    @staticmethod
    def post_comment(user: User, post_id: int, content: str) -> Comment:
        post: Post = Post.objects.get(id=post_id)
        comment: Comment = Comment.objects.create(author=user, post=post, content=content)
        comment.save()
        notification = NetworkModel.create_notification(data = NotificationData(
            sender= user,
            receiver= post.author,
            notification_type= "comment",
            content= comment
        ))
        return comment

    @staticmethod
    def del_comment(user: User, comment_id: int) -> None:
        comment: Comment = Comment.objects.get(pk=comment_id)
        check_permission(user, comment.author)
        comment.delete()

    @staticmethod
    def mark_notifications_as_read(user: User, notif_id: int) -> None:
        notif = Notification.objects.get(pk=notif_id)
        check_permission(user, notif.receiver)
        notif.is_read = True
        notif.save()
        notif.delete()
