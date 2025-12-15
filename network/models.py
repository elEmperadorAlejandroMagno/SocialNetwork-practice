from django.contrib.auth.models import AbstractUser
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

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"
    
    def likes_count(self):
        return self.likes.count()
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un usuario solo puede dar like una vez
        unique_together = ('user', 'post')  

    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"


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
        ('like', 'Like'),
        ('follow', 'Follow'),
        ('comment', 'Comment'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)  # opcional
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def notification_read(self):
        self.is_read = True
        self.save()

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.notification_type})"