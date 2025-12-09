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
