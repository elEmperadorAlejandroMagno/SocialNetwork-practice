from rest_framework import serializers
from .models import Post, Comment
from .utils import likes_count

class BaseContentSerializer(serializers.ModelSerializer):
    formatted_created_at = serializers.CharField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField

    class Meta:
        # El `model` lo define cada subclase
        fields = ["id", "author", "content", "created_at", "formatted_created_at", "likes_count"]

    def get_likes_count(self, obj):
        # Aquí puedes usar tu helper genérico
        return likes_count(obj.__class__.__name__.lower(), obj.id)
    
    def get_is_author(self, obj): 
        request = self.context.get("request") 
        if request and hasattr(request, "user"): 
            return obj.author == request.user.username # o request.user.id si usas FK return False
    

class PostSerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = Post


class CommentSerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = Comment

