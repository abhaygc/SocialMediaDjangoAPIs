from datetime import datetime
from django.db import models
import hashlib

class Users(models.Model):
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=64)
    email = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name+' '+self.email

    def setPassword(self, password):
        self.password = hashlib.sha256(password.encode()).hexdigest()

    def checkPassword(self, password):
        return self.password == hashlib.sha256(password.encode()).hexdigest()
    

class Connections(models.Model):
    following = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='following_user')
    follower = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='follower_user')

class Posts(models.Model):
    title = models.CharField(max_length=200)
    desc = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    author = models.ForeignKey(Users, on_delete=models.CASCADE)

class Comments(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    text = models.TextField()

class Likes(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

