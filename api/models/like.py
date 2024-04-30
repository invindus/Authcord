import uuid

from django.db import models

from .author import Author
from .comment import Comment
from .post import Post
from web_dev_noobs_be.settings import SRV_URL


class Like(models.Model):
    TYPE_CHOICES = (
        ("post", "post"),
        ("comment", "comment"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    object_type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True)
    object_id = models.CharField(max_length=36, null=True)
    published = models.DateTimeField(auto_now_add=True)

    @property
    def type(self):
        return "Like"

    def summary(self):
        if self.author.remote:
            return f"{self.author.remote_name} Likes your {self.object_type}"
        else:
            return f"{self.author.user.username} Likes your {self.object_type}"

    def object_url(self):
        if self.object_type == "post":
            try:
                post = Post.objects.get(uuid=self.object_id)
                author_id = post.author.id
                return f"{SRV_URL}/api/authors/{author_id}/posts/{self.object_id}"
            except Post.DoesNotExist:
                return None
        elif self.object_type == "comment":
            try:
                comment = Comment.objects.get(uuid=self.object_id)
                author_id = comment.author.id
                post_id = comment.post.uuid
                return f"{SRV_URL}/api/authors/{author_id}/posts/{post_id}/comments/{self.object_id}"
            except Comment.DoesNotExist:
                return None
