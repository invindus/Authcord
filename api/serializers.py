import urllib

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from web_dev_noobs_be.settings import SRV_URL
from .models import Author, Post, Notification, Comment, Like, Node


class AuthorSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default="author")
    id = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    displayName = serializers.SerializerMethodField(method_name="get_display_name")
    url = serializers.SerializerMethodField(method_name="get_id")
    profileImage = serializers.URLField(source="profile_image", allow_blank=True)

    @staticmethod
    def get_id(author):
        return f"{AuthorSerializer.get_host(author)}api/authors/{author.id.hex}"

    @staticmethod
    def get_host(author):
        if author.node is not None:
            return author.node.host
        else:
            return SRV_URL + "/"

    @staticmethod
    def get_display_name(author):
        if author.node is not None:
            return author.remote_name
        else:
            return author.user.username

    class Meta:
        model = Author
        fields = ["type", "id", "host", "displayName", "url", "github", "profileImage"]


def author_to_json(author: Author) -> dict | None:
    if author.remote:
        r = author.node.r_get(f"/authors/{author.extern_id}/")
        if r.ok:
            return r.json()
        else:
            return None
    else:
        return AuthorSerializer(author).data


class VisibilityField(serializers.Field):
    def to_internal_value(self, value):
        return Post.Visibility[value]

    def to_representation(self, data):
        return Post.Visibility(data).label


class ContentTypeField(serializers.Field):
    def to_internal_value(self, value):
        return Post.ContentType.from_display(value)

    def to_representation(self, data):
        return Post.ContentType(data).to_display()


class PostSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="post", read_only=True)

    id = serializers.SerializerMethodField()

    source = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()

    title = serializers.CharField()
    description = serializers.CharField()

    content = serializers.CharField()
    contentType = ContentTypeField(source="content_type")

    comments = serializers.SerializerMethodField()
    count = serializers.IntegerField(read_only=True)

    visibility = VisibilityField()
    published = serializers.DateTimeField(read_only=True)

    author = AuthorSerializer(read_only=True)

    @staticmethod
    def get_comments(post):
        return f"{PostSerializer.get_id(post)}/comments"

    @staticmethod
    def get_source(post):
        if post.source == "":
            return PostSerializer.get_id(post)
        else:
            return post.source

    @staticmethod
    def get_origin(post):
        if post.origin == "":
            return PostSerializer.get_id(post)
        else:
            return post.origin

    @staticmethod
    def get_content_type(post):
        return post.get_content_type_display()

    @staticmethod
    def get_visibility(post):
        return post.get_visibility_display()

    @staticmethod
    def get_id(post) -> str:
        return f"{SRV_URL}/api/authors/{post.author.id.hex}/posts/{post.uuid.hex}"

    class Meta:
        model = Post
        fields = ["type", "title", "id", "source", "origin", "description", "contentType", "content", "author", "count",
            "comments", "published", "visibility", ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["data"]


class CommentSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="comment", read_only=True)
    author = AuthorSerializer(read_only=True)
    contentType = serializers.CharField(source="content_type")
    id = serializers.SerializerMethodField()

    @staticmethod
    def get_id(comment) -> str:
        return f"{SRV_URL}/api/authors/{comment.author.id.hex}/posts/{comment.post.uuid.hex}/comments/{comment.uuid.hex}"

    class Meta:
        model = Comment
        fields = ["type", "author", "comment", "contentType", "published", "id"]
        read_only_fields = ["id", "published"]

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)


class LikeSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()
    type = serializers.CharField(default="Like", read_only=True)
    author = AuthorSerializer(read_only=True)
    object = serializers.SerializerMethodField()

    @staticmethod
    def get_summary(like) -> str:
        return like.summary()
    
    @staticmethod
    def get_object(like) -> str:
        return like.object_url()
    
    class Meta:
        model = Like
        fields = ["summary", "type", "author", "object"]

    def create(self, validated_data):
        return Like.objects.create(**validated_data)


def decode_foreign_id(foreign_id):
    decoded = urllib.parse.unquote(foreign_id)
    node_host = "/".join(decoded.split("/")[:-2]) + "/"
    external_id = decoded.split("/")[-1]
    try:
        node = Node.objects.get(host=node_host)
        return node, external_id
    except Node.DoesNotExist:
        return None, external_id
