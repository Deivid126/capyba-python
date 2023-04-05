from rest_framework import serializers
from .models import User,Post
from authcapyba.serializers import UserSerializer

    
class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'is_published', 'author']

class PDFObjSerializer(serializers.Serializer):
    pdf = serializers.FileField()