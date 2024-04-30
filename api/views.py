import base64
import logging
import urllib
from datetime import datetime
from uuid import UUID
import uuid

from web_dev_noobs_be.settings import SRV_URL
import pytz
import requests
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponse,
)
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    inline_serializer,
    OpenApiResponse,
    OpenApiParameter,
)
from rest_framework import serializers
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .models import Notification, Author, Post, Comment, Like, Node
from .serializers import (
    AuthorSerializer,
    NotificationSerializer,
    PostSerializer,
    CommentSerializer,
    LikeSerializer, author_to_json, decode_foreign_id,
)


def get_pagination_data(request):
    page_number = request.GET.get("page")
    size = request.GET.get("size")

    if page_number is None or size is None:
        return False, HttpResponseBadRequest("Page number and size must be provided")

    try:
        page_number = int(page_number)
        if page_number < 1:
            return False, HttpResponseBadRequest("Page number must be greater than 0")
    except ValueError:
        return False, HttpResponseBadRequest("Page number must be an integer")

    try:
        size = int(size)
        if size < 1:
            return False, HttpResponseBadRequest("Size must be greater than 0")
    except ValueError:
        return False, HttpResponseBadRequest("Size must be an integer")

    return page_number, size


class PostView(APIView):
    authentication_classes = [BasicAuthentication]

    @staticmethod
    @extend_schema(
        summary="Retrieve a specific post",
        description="This endpoint is used to get the public post whose id is POST_ID",
        responses={200: PostSerializer, 403: None},  # Specify the response for GET
    )
    def get(request, author_id, post_id):
        author = Author.objects.get(id=author_id)

        post = get_object_or_404(Post, pk=UUID(post_id))

        if Post.Visibility(post.visibility) == Post.Visibility.FRIENDS:
            if (
                post.author.is_friend(request.user)
                or post.author.user == request.user
            ):
                return Response(PostSerializer(post).data, status=HTTP_200_OK)
            else:
                return Response(status=HTTP_403_FORBIDDEN)
        else:
            # if unlisted or public return the post
            return Response(PostSerializer(post).data)

    @staticmethod
    @extend_schema(
        summary="Remove a specific post",
        description="This endpoint is used to remove the  post whose id is POST_ID",
        responses={200: None, 403: None},
        # Specify responses for DELETE
    )
    def delete(request, author_id, post_id):
        post = Post.objects.get(pk=UUID(post_id))

        if request.user == post.author.user:
            post.delete()
            return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_403_FORBIDDEN)

    @staticmethod
    @extend_schema(
        summary="Update a specific post",
        description="This endpoint is used to update a post whose post id is POST_ID",
        request=PostSerializer,
        # Specify request body expected for PUT
        responses={200: None, 400: None, 403: None},  # Specify responses for PUT
    )
    def put(request, author_id, post_id):
        post = Post.objects.get(pk=UUID(post_id))

        if request.user == post.author.user:
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(status=HTTP_200_OK)
            else:
                return Response(status=HTTP_400_BAD_REQUEST)
        else:
            return Response(status=HTTP_403_FORBIDDEN)


class MainPostsView(APIView):
    authentication_classes = [BasicAuthentication]

    @staticmethod
    @extend_schema(
        summary="Create a new post",
        description="This endpoint is use to create a new post with new id",
        request=PostSerializer,
        responses={
            200: PostSerializer,
            400: OpenApiResponse(response="serializer errors"),
            403: OpenApiResponse(
                description="Permission error, invalid user",
                examples=[
                    OpenApiExample(
                        name="PermissionDeniedExample",
                        value={"detail": "Invalid user: [username]"},
                    )
                ],
            ),
        },
    )
    def post(request, author_id):
        try:
            author_id = UUID(author_id)
        except ValueError:
            return Response(status=HTTP_400_BAD_REQUEST)

        author = get_object_or_404(Author, id=author_id)

        if request.user == author.user:
            data = request.data
            serializer = PostSerializer(data=data)
            if serializer.is_valid():
                post = serializer.save(author=author)
                return Response(PostSerializer(post).data, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        else:
            return Response(
                f"invalid user: {request.user.username}", status=HTTP_403_FORBIDDEN
            )

    @staticmethod
    @extend_schema(
        summary="Retrieve paginated list of post from a specific author",
        description="This endpoint is use to get recent posts from author whose id is AUTHOR_ID in paginated form",
        responses={
            200: inline_serializer(
                name="PaginatePostsResponse",
                fields={
                    "type": serializers.CharField(),
                    "items": AuthorSerializer(many=True),
                },
            ),
            404: OpenApiResponse(response="Page not Found"),
        },
    )

    def get(request, author_id):
        page_number, size = get_pagination_data(request)
        if page_number is False:
            return size  # if page_number is False then size is actually a Response object

        try:
            author_id = UUID(author_id)
        except ValueError:
            return HttpResponseNotFound("Invalid author ID")

        author = get_object_or_404(Author, id=author_id)

        if author.remote:
            r = author.node.r_get("authors/" + author.extern_id + f"/posts/?page=1&size=500")
            if not r.ok:
                return Response(r.content, status=r.status_code)
            else:
                posts_data = r.json()
                if isinstance(posts_data, list):
                    return Response({"type": "posts", "items": posts_data}, status=r.status_code)
                if 'items' in posts_data:
                    return Response(posts_data, status=r.status_code)
                else:
                    items = posts_data["posts"]
                    formatted_response = {"type": "posts", "items": items}
                    return Response(formatted_response, status=r.status_code)

        else:
            if not request.user.is_authenticated or not Author.objects.filter(user=request.user).exists():
                paginator = Paginator(Post.objects.filter(author=author, visibility=Post.Visibility.PUBLIC, extern_id = None).order_by("-published"), per_page = size)
            else :
                try:
                        requesting_author = Author.objects.get(user=request.user)
                except Author.DoesNotExist:
                    return HttpResponseNotFound("Requesting author not found")
                if (request.user != author.user):
                    is_friends = requesting_author.is_friend(author)
                    if (is_friends):
                        paginator = Paginator(Post.objects.filter(author=author, visibility__in=[Post.Visibility.PUBLIC, Post.Visibility.FRIENDS]).order_by("-published"), per_page=size)
                    else:
                        if author.remote:
                            if requesting_author.is_following(author):
                                paginator = Paginator(Post.objects.filter(author=author, visibility=Post.Visibility.PUBLIC).order_by("-published"), per_page = size)
                        else:
                            paginator = Paginator(Post.objects.filter(author=author, visibility=Post.Visibility.PUBLIC).order_by("-published"), per_page = size)
                else:

                    paginator = Paginator(Post.objects.filter(author=author).order_by("-published"), per_page=size)


            if page_number <= paginator.num_pages:
                page = paginator.get_page(page_number)  # this is 1-indexed so this is fine
                return JsonResponse(
                    {"type": "posts", "items": [PostSerializer(post).data for post in page]}
                )
            else:
                posts_query = Post.objects.filter(author=author, visibility=Post.Visibility.PUBLIC)

        paginator = Paginator(posts_query.order_by("-published"), per_page=size)
        if page_number <= paginator.num_pages:
            page = paginator.get_page(page_number)
            return JsonResponse(
                {"type": "posts", "items": [PostSerializer(post).data for post in page]}
            )
        else:
            return HttpResponseNotFound("Page not found")


@extend_schema(
    summary="Retrieve paginated list of authors",
    description="This endpoint gets a paginated list of authors ordered by their id. "
    "You can specify the page number and page size with query parameters `page` and `size`.",
    parameters=[
        OpenApiParameter(
            name="page",
            description="Page number of the paginated list",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="size",
            description="Number of items per page",
            required=False,
            type=int,
        ),
    ],
    responses={
        200: inline_serializer(
            name="PaginatedAuthorsResponse",
            fields={
                "type": serializers.CharField(),
                "items": AuthorSerializer(many=True),
            },
        ),
        404: OpenApiResponse(response="Page not Found"),
    },
)


@api_view(["GET"])
def get_all_authors_paginated(request):
    page_number, size = get_pagination_data(request)

    if page_number is False:
        return size  # if page_number is False then size is actually a Response object

    local = request.GET.get("local", None) is not None

    qs = Author.objects.all() if local else Author.objects.filter(node=None)
    qs = qs.order_by("id")

    paginator = Paginator(qs, per_page=size)

    if page_number <= paginator.num_pages:
        page = paginator.get_page(page_number)  # this is 1-indexed so this is fine
        return JsonResponse(
            {
                "type": "authors",
                "items": [AuthorSerializer(author).data for author in page],
            }
        )
    else:
        return HttpResponseNotFound("Page not found")


class SingleAuthorView(APIView):
    @staticmethod
    @extend_schema(
        summary="Retrieve a single author",
        description="This endpoint returns the details of a specific author by their ID.",
        responses={200: AuthorSerializer},
    )
    def get(request, author_id):
        author = Author.objects.get(id=author_id)
        if author.remote:
            r = author.node.r_get("authors/" + author.extern_id + "/")
            if not r.ok:
                return Response(r.content, status=r.status_code)
            else:
                return JsonResponse(r.json(), status=r.status_code)
        else:
            return JsonResponse(AuthorSerializer(author).data)

    @staticmethod
    def put(request, author_id):
        author = get_object_or_404(Author, pk=UUID(author_id))

        # can't edit remote authors
        if author.remote:
            return Response(status=HTTP_403_FORBIDDEN)

        if request.user == author.user:
            display_name = request.data.pop("displayName", None)
            if display_name is not None:
                author.user.username = display_name
                author.user.save()
            serializer = AuthorSerializer(author, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        else:
            return Response(status=HTTP_403_FORBIDDEN)


class FollowersView(APIView):
    @staticmethod
    @extend_schema(
        summary="Retrieve an author's followers",
        description="This endpoint returns a list of followers for a specific author by their ID.",
        responses={
            200: inline_serializer(
                name="FollowersListResponse",
                fields={
                    "type": serializers.CharField(),
                    "items": AuthorSerializer(many=True),
                },
            )
        },
    )
    def get(request, author_id):
        author = Author.objects.get(id=author_id)

        if author.remote:
            r = requests.get(author.node.make_url("authors/" + author.extern_id + "/followers"), auth=(author.node.our_username, author.node.our_password))
            if not r.ok:
                return Response(r.content, status=r.status_code)
            else:
                return JsonResponse(r.json(), status=r.status_code)
        else:

            fds = [AuthorSerializer(follower).data for follower in author.followers.all()]
            return JsonResponse(
                {
                    "type": "followers",
                    "items": fds,
                }
            )


class ForeignFollowerView(APIView):
    @staticmethod
    @extend_schema(
            summary="Check if a foreign author follows the current author",
            description="This endpoint checks if a foreign author follows the current author.",
            responses={
                200: None,
                404: None,
            },
    )
    def get(request, author_id, foreign_id):
        author = get_object_or_404(Author, pk=UUID(author_id))
        node, extern_id = decode_foreign_id(foreign_id)
        if author.remote:
            r = author.node.r_get(f"/authors/{author.extern_id}/followers/{foreign_id}")
            if r.ok and author.is_followed_by(extern_id):
                return Response(status=r.status_code)
            
            return Response(status=status.HTTP_404_NOT_FOUND)
      
        if node is None:
            if author.is_followed_by(extern_id):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            foreign_author = Author.objects.get(extern_id = extern_id)
            if author.is_followed_by(foreign_author.id):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @extend_schema(
        summary="Follow a foreign author.",
        description="This endpoint allows the current author to follow a foreign author.",
        responses={
            200: None,
            409: None,
        },
    )
    def put(request, author_id, foreign_id):
        author = get_object_or_404(Author, pk=UUID(author_id))

        if not author.remote and request.user != author.user:
            return Response({"message": f"Must be authenticated as author {author.id.hex}!"},
                            status=status.HTTP_403_FORBIDDEN)

        node, extern_id = decode_foreign_id(foreign_id)

        if node is None:
            other_author = get_object_or_404(Author, pk=UUID(extern_id))
            if author.is_followed_by(other_author.id):
                return Response(status=status.HTTP_409_CONFLICT)
            else:
                other_author.follow(author)
                return Response({"message": "Followed local author"}, status=status.HTTP_200_OK)

        foreign_author = Author.objects.filter(node=node, extern_id=extern_id).first()

        if author.is_followed_by(foreign_author.id):
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            foreign_author.follow(author)
            return Response({"message": "Followed remote author"}, status=status.HTTP_200_OK)

    @staticmethod
    @extend_schema(
        summary="Unfollow a foreign author.",
        description="This endpoint allows the current author to unfollow a foreign author.",
        responses={
            200: None,
        },
    )
    def delete(request, author_id, foreign_id):
        author = get_object_or_404(Author, pk=UUID(author_id))
        node, extern_id = decode_foreign_id(foreign_id)

        # TODO authentication
        if node is None:
            other_author = get_object_or_404(Author, pk=UUID(extern_id))
            author.remove_follower(other_author)
            logging.getLogger(__name__).debug(f"""
            [{author.a_name}].remove_follower([{other_author.a_name}])
            """)
            return Response(status=status.HTTP_200_OK)

class InboxView(APIView):
    def get_authenticators(self):
        try:
            if self.request and self.request.method in ["GET", "DELETE"]:
                return [BasicAuthentication()]
        except AttributeError:
            # This is mainly for DRF-Spectacular schema generation
            return []
        return []

    @staticmethod
    def create_notification(recipient, content_type, content):
        Notification.objects.create(
            recipient=recipient, type=content_type, data=content
        )

    @staticmethod
    def create_comment(item, author):
        object_id= item["id"]
        object_parts= object_id.split('/')
        index = object_parts.index("posts")
        post_id = object_parts[index+1]
        post = Post.objects.get(uuid=post_id)
        comment_id = object_parts[-1]
        Comment.objects.get_or_create(
            comment = item["comment"],
            content_type = item["contentType"],
            author = author,
            post = post,
            extern_id = comment_id
        )


    @staticmethod
    def create_like(item, author):
        obj = item['object']
        post_id = obj.split('/').pop()
        summary = item["summary"]
        parts = summary.split(" ")
        if parts[-1] == "post":
            object_type = "post"
        else:
            object_type = "comment"
        Like.objects.get_or_create(
            object_id=post_id, author=author, object_type=object_type
        )

    @staticmethod
    def create_post(item, author):
        post_url = item["id"]
        post_id = post_url.split('/').pop()
        content_type_code = Post.ContentType.from_display(item["contentType"]).value
        visibility = item["visibility"].upper()
        visibility_code = Post.Visibility[visibility].value
        existing_post = Post.objects.filter(extern_id=post_id).first()

        if existing_post:
            return existing_post, False
        else:
            post = Post.objects.create(
                title=item["title"],
                description=item["description"],
                content=item["content"],
                content_type=content_type_code,
                visibility=visibility_code,      # Use the converted one-character code
                author=author,
                extern_id=post_id
            )
            return post, True


    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["post", "Like", "comment", "follow"],
                    },
                    "content": {
                        "type": "string",
                    },
                },
                "required": ["type", "content"],
            },
        },
        responses={
            201: OpenApiResponse(
                response="Content Type Notification created successfully and sent to the author"
            ),
            406: OpenApiResponse(
                response="The type can only be post, comment, like, or follow"
            ),
        },
        summary="Create a notification",
        description="This endpoint is used to create a notification for an author depending on the type",
    )
    def post(self, request, author_id):
        author = get_object_or_404(Author, id=author_id)
        data = request.data
        r_type = data["type"].lower()
        print(data)
        if author.remote:
            url = "authors/" + author.extern_id + "/inbox"
            if r_type == "follow":
                sending_author_url = data["actor"]["id"]
                sending_author_id = sending_author_url.split('/').pop()
                sending_author = Author.objects.get(id=UUID(sending_author_id))

                if author.is_followed_by(sending_author_id):
                    return Response("Follow request already sent", status=status.HTTP_409_CONFLICT)
                else:
                    sending_author.follow(author)
                    

            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"""
            POSTING TO {author.remote_name + "(remote)"}:
            {request.data}
            ===========================================
            @ {author.node.make_url(url)}
            ===========================================
            """)
            headers = {"Content-Type": "application/json", }
            print (url)
            r = author.node.r_post(url, json=data, headers=headers, auth=(author.node.our_username, author.node.our_password))
            return HttpResponse(status=r.status_code, content=r.content, content_type=r.headers["Content-Type"])
        else:

            
            data["type"] = r_type
            valid_types = ["post", "like", "comment", "follow"]
            if r_type not in valid_types:
                return Response(
                    "The type can only be post, comment, Like, or Follow",
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            
            if r_type != "follow":
                posting_author_url = data["author"]["id"]
                posting_author_id = posting_author_url.split('/').pop()
                try:
                    posting_author = Author.objects.get(id=UUID(posting_author_id))
                except (ValueError, Author.DoesNotExist):
                    try:
                        posting_author = Author.objects.get(extern_id=posting_author_id)
                    except Author.DoesNotExist:
                        return Response(
                            f"Author not found with either id or extern_id matching: {posting_author_id}",
                            status=status.HTTP_404_NOT_FOUND)
                if posting_author.remote:
                    if data["type"] == "post":
                        post, created= self.create_post(data, posting_author)
                        if not created:
                            return Response("Post already exists", status=status.HTTP_409_CONFLICT)
                        elif post is None:
                            return Response("Post was not created", status=status.HTTP_404_NOT_FOUND)

                    elif data["type"] == "comment":
                        self.create_comment(data, posting_author)
                    elif data["type"] == "like":
                        self.create_like(data, posting_author)



            self.create_notification(
                    recipient=author, content_type=r_type, content=data
                )

            return Response(
                f"{r_type} Notification created successfully and sent to {author.user.username}",
                status=status.HTTP_200_OK
            )

    @extend_schema(
        responses={
            200: inline_serializer(
                name="InboxResponse",
                fields={
                    "type": serializers.CharField(),
                    "author": serializers.CharField(),
                    "items": NotificationSerializer(many=True),
                },
            ),
            404: OpenApiResponse(response="Page not found"),
        },
        description="This endpoint is used to retrieve paginated inbox notifications for an author",
        summary="Get the inbox of notifications",
    )
    def get(self, request, author_id):
        author = get_object_or_404(Author, id=author_id)
        page_number, size = get_pagination_data(request)

        if page_number is False:
            return size

        notifications_query = Notification.objects.filter(recipient=author).order_by(
            "-created_at"
        )
        paginator = Paginator(notifications_query, per_page=size)

        if page_number <= paginator.num_pages:
            page = paginator.get_page(page_number)
            # this is 1-indexed so this is fine
            items = []

            for notification in page:
                serializer = NotificationSerializer(notification)
                notification_data = serializer.data
                items.append(notification_data["data"])
            data = {
                "type": "inbox",
                "author": AuthorSerializer(author).get_id(author),
                "items": items
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return HttpResponseNotFound("Page not found")

    @extend_schema(
        responses={
            200: OpenApiResponse(response="Inbox Cleared"),
            204: OpenApiResponse(response="No notification in inbox to clear"),
        },
        summary="Clear the inbox",
        description="Thi endpoint is used to clear notifications in the inbox except posts",
    )
    def delete(self, request, author_id):
        author = get_object_or_404(Author, id=author_id)
        deleted_count, items = Notification.objects.filter(recipient=author).delete()
        if deleted_count > 0:
            return Response("Inbox Cleared", status=status.HTTP_200_OK)

        return Response(
            "No notification in inbox to clear", status=status.HTTP_204_NO_CONTENT
        )


class CommentList(APIView):
    @extend_schema(
        responses={200: CommentSerializer(many=True)},
        description="This endpoint is used to retrieve a list of comments for a given post, ordered by their "
        "publication date in descending "
        "order.",
        summary="Retrieve comments on a specific post",
    )
    def get(self, request, author_id, post_id):
        page_number, size = get_pagination_data(request)
        author = Author.objects.get(id =author_id)
        post = get_object_or_404(Post, uuid=post_id, author__id=author_id)
        if author.remote:
            r = requests.get(author.node.make_url(f"authors/{author.extern_id}/posts/{post.extern_id}/comments?page={page_number}&size={size}"), auth=(author.node.our_username, author.node.our_password))
            if not r.ok:
                return Response(r.content, status=r.status_code)
            else:
                return JsonResponse(r.json(), status=r.status_code)
        else:
            comments_query = Comment.objects.filter(post=post).order_by("-published")
            if page_number is False:
                return size

            paginator = Paginator(comments_query, per_page=size)

            if page_number <= paginator.num_pages:
                page = paginator.get_page(page_number)
                # this is 1-indexed so this is fine
                comments = []
                for comment in page:
                    serializer = CommentSerializer(comment)
                    comment_data = serializer.data
                    comments.append(comment_data)

                data = {
                    "type": "comments",
                    "page": page_number,
                    "size": size,
                    "post": PostSerializer(post).get_id(post),
                    "id" : PostSerializer(post).get_id(post) + "comments",
                    "comments": comments
                }

                return Response(data, status=status.HTTP_200_OK)
            else:
                return HttpResponseNotFound("404 not found")


    @extend_schema(
        request=CommentSerializer,
        responses={201: CommentSerializer, 400: None},
        description="This endpoint is used to add a new comment on specific post",
        summary="Create a new comment",
    )
    def post(self, request, author_id, post_id):
        if isinstance(request.user.author, AnonymousUser):
            return Response(status=status.HTTP_403_FORBIDDEN)

        
        author = get_object_or_404(Author, id = author_id)
        serializer = CommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            comment = serializer.save(
                author=request.user.author, post=get_object_or_404(Post, uuid=post_id)
            )
            if author.remote:
                posting_author = get_object_or_404(Author, id = request.user.author.id)
                author_serializer = AuthorSerializer(posting_author).data
                post = Post.objects.get(uuid = post_id)
                body = {
                    "type": "comment",
                    "author": author_serializer,
                    "comment": request.data.get("comment"),
                    "contentType": request.data.get("contentType"),
                    "published": datetime.now().isoformat() + "Z",
                    "id": author.node.make_url(f"authors/{author.extern_id}/posts/{post.extern_id}/comments/{comment.uuid}")
                }
                print (body)

                r = requests.post(author.node.make_url(f"authors/{author.extern_id}/inbox"),json=body, auth=(author.node.our_username,author.node.our_password))
                if not r.ok:
                    return Response(r.content, status=r.status_code)
                return Response({"message": "Comment successfully posted to remote author."}, status=status.HTTP_201_CREATED)
            else:
                Notification.objects.create(recipient=author,data=serializer.data,type="comment")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class  LikePostView(APIView):


    @extend_schema(
        responses={200: LikeSerializer(many=True)},
        description="This endpoint is used to retrieve all likes for a specific post.",
        summary="Retrieve likes for a post",
    )
    def get(self, request, author_id, post_id):
        author = Author.objects.get(id=UUID(author_id))
        post = Post.objects.get(uuid =UUID(post_id))
        if author.remote:
            r = requests.get(author.node.make_url(f"authors/{author.extern_id}/posts/{post.extern_id}/likes"), auth=(author.node.our_username, author.node.our_password))
            if not r.ok:
                return Response(r.content, status=r.status_code)
            else:
                like_data = r.json()
                if isinstance(like_data, list):
                    formatted_response = {"type": "Like", "items": like_data}
                    return Response(formatted_response, status=r.status_code) 
                else:
                    return JsonResponse(r.json(), status=r.status_code)
        else:
            likes = Like.objects.filter(object_id=post_id, object_type="post")
            serializer = LikeSerializer(likes, many=True)
            return JsonResponse({"type" : "Like" ,
                                "items": serializer.data})

    @extend_schema(
        request=None,  # Assuming no request body for POST
        responses={
            201: None,  # No content for successful like addition
            409: OpenApiResponse(response="Already Liked"),
        },
        description="This endpoint is used to add a like to a specific post.",
        summary="Create a new like on post",
    )
    def post(self, request, author_id, post_id):
        id= request.data.get('id')
        author = get_object_or_404(Author, id = id)
        inbox_author = get_object_or_404(Author, id = author_id)
        if inbox_author.remote:
            post = Post.objects.get(uuid = post_id)
            author_serializer = AuthorSerializer(author).data
            body = {
                
                "summary": f"{author.user.username} Likes your post",
                "type": "Like",
                "author": author_serializer,
                "object": inbox_author.node.make_url(f"authors/{inbox_author.extern_id}/posts/{post.extern_id}"),
            }
            r = requests.post(inbox_author.node.make_url(f"authors/{inbox_author.extern_id}/inbox"),json=body,auth=(inbox_author.node.our_username,inbox_author.node.our_password))
            if not r.ok:
                return Response(r.content, status=r.status_code)
            else:
                return Response(status=r.status_code)
            
        else:
            like, created = Like.objects.get_or_create(
                object_id=post_id, author=author, object_type="post"
            )
            if created:
                serializer = LikeSerializer(like)
                Notification.objects.create(recipient=inbox_author,data=serializer.data,type="Like")
                return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Already liked"}, status=status.HTTP_409_CONFLICT)


class LikeCommentView(APIView):
    authentication_classes = [BasicAuthentication]

    @extend_schema(
        responses={200: LikeSerializer(many=True)},
        description="This endpoint is used to retrieve all likes for a specific comment.",
        summary="Retrieve likes for comment",
    )

    def get(self, request, author_id, post_id, comment_id):


        try:
            post = Post.objects.get(uuid=UUID(post_id))
        except Post.DoesNotExist:
            try:
                post = Post.objects.get(extern_id=post_id)
            except Author.DoesNotExist:
                return Response(
                    f"Post not found with either id or extern_id matching: {post_id}",)
            
        try:
            author = Author.objects.get(id=UUID(author_id))
        except Author.DoesNotExist:
            try:
                author = Author.objects.get(extern_id=author_id)
            except Author.DoesNotExist:
                return Response(
                    f"Author not found with either id or extern_id matching: {author_id}",)
        print (comment_id)
        

        if Comment.objects.filter(uuid = comment_id).exists():
            comment = Comment.objects.get(uuid=comment_id)
            if comment.author.remote:
                print("i was here i am remote")
                r = requests.get(comment.author.node.make_url(f"authors/{author.id}/posts/{post.uuid}/comments/{comment.extern_id}/likes"), auth=(comment.author.node.our_username,comment.author.node.our_password))
                if not r.ok:
                    return Response(r.content, status=r.status_code)
                else:
                    likes_data = r.json()
                    if isinstance(likes_data, list):
                        return Response({"type": "Like", "items": likes_data}, status=r.status_code)
                    else:
                        return Response(likes_data,status=r.status_code)
            else:
                print("i was here")
                likes = Like.objects.filter(object_id=comment_id, object_type="comment")
                serializer = LikeSerializer(likes, many=True)
                return JsonResponse({"type" : "Like" ,
                                    "items": serializer.data})
               
        else:
            r = requests.get(author.node.make_url(f"authors/{author.extern_id}/posts/{post.extern_id}/comments/{comment_id}/likes"), auth=(author.node.our_username, author.node.our_password))
            if not r.ok:
                return Response(r.content, status=r.status_code)
            else:
                likes_data = r.json()
                if isinstance(likes_data, list):
                    return Response({"type": "Like", "items": likes_data}, status=r.status_code)
                else:
                    return Response(likes_data,status=r.status_code)

    @extend_schema(
        request=None,
        responses={201: None, 409: OpenApiResponse(response="Already Liked")},
        description="This endpoint is used to add a like to a specific comment. Returns 409 if already liked.",
        summary="Post like to comment",
    )
    def post(self, request, author_id, post_id, comment_id):
        logged_author = request.user.author
        commentor_url = request.data.get("commentAuthorUrl")
        commentor_id = commentor_url.split('/').pop()
        print(commentor_id)

        try:
            commenting_author= Author.objects.get(id=UUID(commentor_id))
        except Author.DoesNotExist:
            try:
                commenting_author = Author.objects.get(extern_id=commentor_id)
            except Author.DoesNotExist:
                return Response(
                    f"Author not found with either id or extern_id matching: {commentor_id}",)

        
            
        try:
            post = Post.objects.get(uuid=UUID(post_id))
        except Post.DoesNotExist:
            try:
                post = Post.objects.get(extern_id=post_id)
            except Author.DoesNotExist:
                return Response(
                    f"Post not found with either id or extern_id matching: {post_id}",)
        
        if commenting_author.remote:
            print (True)
            author_serializer = AuthorSerializer(logged_author).data
            if post.extern_id is None:
                comment = Comment.objects.get(uuid = comment_id)

                body = {
                    "summary": f"{logged_author.user.username} likes your comment",
                    "type": "Like",
                    "author": author_serializer,
                    "object": commenting_author.node.make_url(f"authors/{commenting_author.extern_id}/posts/{post.uuid}/comments/{comment.extern_id}"),
                }
            else:
                body = {
                    "summary": f"{logged_author.user.username} likes your comment",
                    "type": "Like",
                    "author": author_serializer,
                    "object": commenting_author.node.make_url(f"authors/{commenting_author.extern_id}/posts/{post.extern_id}/comments/{comment_id}"),
                }

            print (body)
            r = requests.post(commenting_author.node.make_url(f"authors/{commenting_author.extern_id}/inbox"),json=body,auth=(commenting_author.node.our_username,commenting_author.node.our_password))
            if not r.ok:
                return Response(r.content, status=r.status_code)
            else:
                return Response(r.json(), status=r.status_code)
        else:
            print("should not be here")
            like, created = Like.objects.get_or_create(
                object_id=comment_id, author=logged_author, object_type="comment"
            )
            if created:
                serializer = LikeSerializer(like)
                Notification.objects.create(recipient=commenting_author,data=serializer.data,type="Like")
                return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Already liked"}, status=status.HTTP_409_CONFLICT)

          


class GetAuthorLikedAPIView(APIView):
    authentication_classes = [BasicAuthentication]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="A list of items liked by the author",
                response="Liked Items",
            )
        },
        description="This endpoint is used to retrieve items liked by a specific author.",
        summary="Retrieves author likes",
    )
    def get(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author not found"}, status=404)

        likes_by_author = Like.objects.filter(author=author)
        liked_posts_comments = []

        for like in likes_by_author:
            item = LikeSerializer(like)
            liked_posts_comments.append(item.data)

        response = {
            "type": "Liked",
            "items": liked_posts_comments
        }

        return Response(response, status=status.HTTP_200_OK)


@api_view(["GET"])
def image_post_view(request, author_id, post_id):
    post = get_object_or_404(Post, pk=UUID(post_id))
    if not post.is_image():
        return Response(status=status.HTTP_404_NOT_FOUND)

    return HttpResponse(
        base64.b64decode(post.content),
        status=status.HTTP_200_OK,
        content_type=post.get_content_type_display().rstrip(";base64"),
    )
