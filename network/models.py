from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.CharField(max_length=20)
    content = models.CharField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.BigIntegerField(default=0)

class Follower(models.Model):
    follows = models.CharField(max_length=100)
    follower = models.CharField(max_length=100)

class Like(models.Model):
    user = models.CharField(max_length=100)
    post = models.BigIntegerField(default=0)
