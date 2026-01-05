from rest_framework import serializers
from .models import Post, Comment
from .utils import likes_count

class BaseContentSerializer(serializers.ModelSerializer):
    formatted_created_at = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        # El `model` lo define cada subclase
        fields = ["id", "author", "content", "created_at", "formatted_created_at", "is_author", "likes_count"]

    def get_formatted_created_at(self, obj): # Usamos la propiedad del modelo o lo calculamos aquí 
        return obj.formatted_created_at

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

