from dataclasses import dataclass
from .models import Post, User, Follow, Notification, Like, Comment
from .utils import check_permission, CONTENT_TYPE, likes_count, load_like_state
from django.db.models.query import QuerySet
from django.utils.formats import date_format

@dataclass
class BaseResponse:
    id: int
    author: str
    content: str
    likes_count: int
    created_at: str

@dataclass
class NewPostResponse:    
    """
    Representa la estructura de la respuesta al crear un nuevo post.
    """
    status: str
    new_post: BaseResponse
    is_author: bool

@dataclass
class NewCommentResponse:
    status: str
    new_comment: BaseResponse
    is_author: bool
    


class NetworkModel:

    @staticmethod
    def get_all_posts(user) -> QuerySet[Post]:
        posts = Post.objects.all().order_by("-created_at")
        return load_like_state(posts, user)
    
    @staticmethod
    def get_all_following_posts(user: User) -> QuerySet[Post]:
        following_users = [follow.following for follow in Follow.objects.filter(follower=user)]
        posts = Post.objects.filter(author__in=following_users).order_by("-created_at")
        return load_like_state(posts, user)
    
    @staticmethod
    def get_user_posts(user: User) -> QuerySet[Post]:
        posts = Post.objects.filter(author=user).order_by("-created_at")
        return load_like_state(posts, user)
    

    @staticmethod
    def get_post_by_id(post_id: int) -> tuple[Post, QuerySet[Comment]]:
        post = Post.objects.get(id=post_id)
        comments = post.comments.all().order_by("-created_at") #type: ignore
        return post, comments
    
    @staticmethod
    def create_new_post(user: User, content: str) -> NewPostResponse:
        post: Post = Post.objects.create(author=user, content=content)
        post.save()

        response_data = NewPostResponse(
            status= "success",
            new_post = BaseResponse(
                id = post.pk,
                author=  user.username,
                content= post.content,
                likes_count= likes_count("post", post.pk),
                # Formatear igual que en los templates de Django
                created_at= date_format(post.created_at, format='N j, Y, P', use_l10n=True),
            ),
            is_author= True 
        )
        return response_data

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
            if content_type == 'post':
                post = Post.objects.get(pk=object_id)
                Notification.objects.create(
                    sender=user,
                    receiver=post.author,
                    notification_type='like',
                    post=post
                )
            elif content_type == 'comment':
                comment = Comment.objects.get(pk=object_id)
                Notification.objects.create(
                    sender=user,
                    receiver=comment.author,
                    notification_type='like',
                    comment=comment,
                )
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
            Notification.objects.create(
                sender=follower,
                receiver=user_to_follow,
                notification_type='follow'
            )

        followers_count: int = user_to_follow.followers_count()
        return followers_count, action

    @staticmethod
    def post_comment(user: User, post_id: int, content: str) -> NewCommentResponse:
        post: Post = Post.objects.get(id=post_id)
        comment: Comment = Comment.objects.create(author=user, post=post, content=content)
        comment.save()

        new_comment = NewCommentResponse( 
            status = "success",
            new_comment = BaseResponse(
                id = comment.pk,
                author = user.username,
                content = comment.content,
                likes_count = likes_count("comment", comment.pk),
                created_at = date_format(comment.created_at, format='N j, Y, P', use_l10n=True),
            ),
            is_author = True
        )
        return new_comment

    @staticmethod
    def del_comment(user: User, comment_id: int) -> None:
        comment: Comment = Comment.objects.get(pk=comment_id)
        check_permission(user, comment.author)
        comment.delete()