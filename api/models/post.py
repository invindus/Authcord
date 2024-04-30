from __future__ import annotations

import uuid

from django.db import models

from .author import Author


class Post(models.Model):
    """
    Represents some post by some local user.
    """

    class ContentType(models.TextChoices):
        """
        One-character codes for content types, with descriptive text.
        """

        PLAIN = "t", "text/plain"
        MARKDOWN = "m", "text/markdown"
        BASE64 = "b", "application/base64"
        PNG = "p", "image/png;base64"
        JPEG = "j", "image/jpeg;base64"

        @staticmethod
        def from_display(display: str) -> Post.ContentType:
            match display:
                case "text/plain":
                    return Post.ContentType.PLAIN
                case "text/markdown":
                    return Post.ContentType.MARKDOWN
                case "application/base64":
                    return Post.ContentType.BASE64
                case "image/png;base64":
                    return Post.ContentType.PNG
                case "image/jpeg;base64":
                    return Post.ContentType.JPEG

        def to_display(self) -> str:
            match self:
                case Post.ContentType.PLAIN:
                    return "text/plain"
                case Post.ContentType.MARKDOWN:
                    return "text/markdown"
                case Post.ContentType.BASE64:
                    return "application/base64"
                case Post.ContentType.PNG:
                    return "image/png;base64"
                case Post.ContentType.JPEG:
                    return "image/jpeg;base64"

    class Visibility(models.TextChoices):
        """
        One-character codes for content types, with descriptive text.
        """

        PUBLIC = "p", "PUBLIC"
        FRIENDS = "f", "FRIENDS"
        UNLISTED = "u", "UNLISTED"

    def is_image(self):
        return (
            self.content_type == Post.ContentType.PNG
            or self.content_type == Post.ContentType.JPEG
        )

    # Unique identifier for each post, using UUID.
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()

    source = models.URLField(max_length=1024, blank=True)
    origin = models.URLField(max_length=1024, blank=True)
    extern_id = models.CharField(max_length=1024, blank=True, null = True)
    

    description = models.TextField(null=True)

    content_type = models.CharField(choices=ContentType.choices, max_length=1)
    content = models.TextField()

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="posts")

    count = models.IntegerField(default=0)
    comments = models.URLField(blank=True)

    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(choices=Visibility.choices, max_length=1)

    def __str__(self):
        username = self.author.user.username if self.author.user else 'Remote Author'
        return f"Post {self.uuid.hex} [by {username}]" 
