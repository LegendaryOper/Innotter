from django.db import models
import uuid

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.UUIDField(primary_key=False, editable=True, default=uuid.uuid4)
    description = models.TextField()
    tags = models.ManyToManyField('innotter_functional.Tag', related_name='pages', blank=True)
    owner = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='pages')
    followers = models.ManyToManyField('user.User', related_name='follows', blank=True)
    image = models.URLField(null=True, blank=True)
    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField('user.User', related_name='requests', blank=True)
    unblock_date = models.DateTimeField(null=True, blank=True)


class Post(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=180)
    reply_to = models.ForeignKey('innotter_functional.Post', on_delete=models.SET_NULL, null=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=180)


