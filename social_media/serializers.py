from rest_framework import serializers
from .models import Users, Connections, Posts, Comments, Likes
# import hashlib

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'name', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            # instance.password = hashlib.sha256(password.encode()).hexdigest()
            instance.setPassword(password)
        instance.save()
        return instance
class ConnectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connections
        fields = ['id','following','follower']

class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id', 'title', 'desc', 'created_at', 'author']

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id', 'post', 'user', 'text']

class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ['id', 'post', 'user']