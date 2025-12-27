from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models

# extender la clase User por defecto de Django
# configurar en settings.py
class User(AbstractUser):
    
    def followers_count(self):
        return self.followers.count()
    
    def following_count(self):
        return self.following.count()

# POST model
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # relación genérica para poder consultar likes desde Post (por ejemplo: post.likes.count())
    likes = GenericRelation('Like')

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"
    
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un usuario solo puede dar like una vez
        unique_together = ('user', 'content_type', 'object_id')
    
    @classmethod
    def likes_count(cls, model, id):
        return cls.objects.filter(content_type=model, object_id=id).count()

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = GenericRelation('Like')


# Following model
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # evita datos duplicados
        unique_together = ('follower', 'following')


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like_post', 'Like Post'),
        ('like_comment', 'Like Comment'),
        ('follow', 'Follow'),
        ('comment', 'Comment'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)  # opcional
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True) #opcional
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def notification_read(self):
        self.is_read = True
        self.save()

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.notification_type})"