import uuid

from django.db import models

from .author import Author
from .node import Node
from .post import Post


class Comment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    extern_id = models.CharField(max_length=1024, null=True, blank=True)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, null=True, blank=True)

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comments"
    )
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="author_comments"
    )
    comment = models.TextField()
    content_type = models.CharField(
        max_length=100, choices=Post.ContentType.choices, default=Post.ContentType.PLAIN
    )
    published = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.author.user.username if self.author.user else self.author.remote_name
        return f"Comment {self.uuid.hex} [by {username}]"
