import urllib
from datetime import datetime
from uuid import UUID

import pytz
import requests
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Post, Author, Notification, Node, Comment
from api.serializers import PostSerializer, author_to_json, CommentSerializer, AuthorSerializer
from web_dev_noobs_be.settings import SRV_URL


# TODO remote
@api_view(["GET"])
@authentication_classes([BasicAuthentication])
def author_post_count(request, author_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    count = Post.objects.filter(author__id=UUID(author_id)).count()
    return Response({"count": count}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([BasicAuthentication])
def post_count(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.user.author is None:
        return Response(status=status.HTTP_403_FORBIDDEN)

    followers_posts = Post.objects.filter(visibility=Post.Visibility.FRIENDS, author__followers=request.user.author)
    public_count = Post.objects.filter(visibility=Post.Visibility.PUBLIC).count()
    count = public_count

    for p in followers_posts:
        if p.author.is_friend(request.user):
            count += 1

    return Response({"count": count}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([BasicAuthentication])
def comments(request, foreign_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    foreign_id = urllib.parse.unquote(foreign_id)
    if foreign_id[-1] == "/":
        foreign_id = foreign_id[:-1]
    xs = foreign_id.split("/")
    post_id = xs[-1]
    author_id = xs[-3]

    host = "/".join(xs[:-4]) + "/"

    id_postfix = "/".join(xs[-4:])

    page = 1
    size = 100
    if host == SRV_URL + "/api/":
        post = get_object_or_404(Post, uuid=UUID(post_id))
        comments_query = Comment.objects.filter(post=post).order_by("-published")
        c_data = []
        for c in comments_query:
            c_data.append(CommentSerializer(c).data)
        return JsonResponse({"comments": c_data}, status=status.HTTP_200_OK)
    else:
        author = get_object_or_404(Author, node__host=host, extern_id=author_id)
        r = author.node.r_get(f"/{id_postfix}/comments?size={size}&page={page}")
        return JsonResponse(r.json(), status=status.HTTP_200_OK)


class GetGithubActivity(APIView):
    authentication_classes = [BasicAuthentication]

    @staticmethod
    def create_post(description, content, author):
        Post.objects.create(
            title="Github Event",
            description=description,
            content=content,
            author=author,
            visibility=Post.Visibility.PUBLIC,
            content_type=Post.ContentType.PLAIN
        )

    @staticmethod
    def get_content(e):
        content = None
        match e["type"]:
            case "WatchEvent":
                content = f"{e['payload']['action']} watching the repo {e['repo']['name']}",
            case "CreateEvent":
                content = f"New {e['payload']['ref_type']} has been created from {e['payload']['master_branch']}"
            case "DeleteEvent":
                content = f"{e['payload']['ref_type']} has been deleted from {e['repo']['name']}"
            case "ForkEvent":
                content = f"Forked repository from {e['repo']['name']}"
            case "IssuesEvent":
                content = f"{e['payload']['action']} an issue",
            case "MemberEvent":
                content = f"{e['payload']['action']} a new member: {e['payload']['member']['login']}"
            case "PublicEvent":
                content = f"{e['repo']['name']} is now public"
            case "PullRequestEvent":
                content = f"Pull request {e['payload']['number']} has been {e['payload']['action']}"
            case "PushEvent":
                content = f"commits pushed to {e['repo']['name']}"
        return content

    @extend_schema(
        summary="Fetch GitHub activity",
        description="This endpoint is used to fetch GitHub activity for a specific author and create posts based on "
                    "the events.",
        responses={
            200: OpenApiResponse(description="New posts created successfully"),
            204: OpenApiResponse(description="No new events created since last update"),
            400: OpenApiResponse(description="Unable to fetch the GitHub events"),
        },
    )
    def get(self, request, author_id):
        author = get_object_or_404(Author, id=author_id)
        try:
            post = Post.objects.filter(title="Github Event", author=author).latest('published')
            last_get_date = post.published
        except Post.DoesNotExist:
            last_get_date = None

        github_url = author.github
        github_username = github_url.split('/').pop()

        url = "https://api.github.com/users/" + github_username + "/events/public"

        response = requests.get(url)

        if response.status_code == 200:
            all_events = response.json()
            new_events = [
                event for event in all_events
                if last_get_date is None or datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(
                    tzinfo=pytz.UTC) > last_get_date
            ]
            if len(new_events) != 0:
                for event in new_events:
                    content = GetGithubActivity.get_content(event)
                    if content is not None:
                        self.create_post(description=event['type'], content=content, author=author)
            else:
                return Response("No new events created since last update", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("Unable to fetch the github events", status=status.HTTP_400_BAD_REQUEST)
        return Response("New posts created successfully", status=status.HTTP_200_OK)


class RequestsView(APIView):
    @staticmethod
    def delete(request, foreign_id):
        actor_id = urllib.parse.unquote(foreign_id)

        request = get_object_or_404(Notification, data__actor__id=actor_id, recipient__user=request.user)
        request.delete()

        return Response(status=status.HTTP_200_OK)


class RemoteAuthorsScan(APIView):
    @staticmethod
    def get(request):
        all_nodes = Node.objects.all()
        for node in all_nodes:
            r = node.r_get("authors/?page=1&size=200")
            if not r.ok:
                continue
            data = r.json()
            authors = data.get('items', [])
            print(authors)
            for author in authors:
                author_id = author['id'].split('/').pop()
                _, created = Author.objects.get_or_create(
                    extern_id=author_id,
                    node=node,
                    remote_name=author.get("displayName"),
                )
        return Response({"message": "Authors fetched successfully"}, status=status.HTTP_200_OK)


class GlobalPostsView(APIView):
    authentication_classes = [BasicAuthentication]

    @staticmethod
    def get(request):
        # fetching all posts initially
        posts_query = Post.objects.all().order_by("-published")
        page_size = request.query_params.get('size', 40)
        page_number = request.query_params.get('page', 1)

        if request.user.is_authenticated:
            try:
                requesting_author = Author.objects.get(user=request.user)
                # filtering posts based on visibility and friends
                filtered_posts = []
                for post in posts_query:
                    if post.visibility == Post.Visibility.PUBLIC:
                        filtered_posts.append(post)
                    elif post.visibility == Post.Visibility.FRIENDS and requesting_author.is_friend(post.author):
                        filtered_posts.append(post)
                    elif post.author == requesting_author:
                        # showing all posts if author is viewing their own posts
                        filtered_posts.append(post)
                posts_query = filtered_posts
            except Author.DoesNotExist:
                # if requesting author not found shows only public posts
                posts_query = posts_query.filter(visibility=Post.Visibility.PUBLIC)
        else:
            # show only public posts if user not authenticated
            posts_query = posts_query.filter(visibility=Post.Visibility.PUBLIC)

        paginator = Paginator(posts_query, page_size)
        try:
            page_obj = paginator.page(page_number)
        except ValueError:
            return HttpResponseNotFound("Pagination error")

        serialized_posts = PostSerializer(page_obj.object_list, many=True)
        return JsonResponse({"type": "posts", "items": serialized_posts.data})


class AuthorFollowersView(APIView):
    @staticmethod
    def get(request, author_id):
        author = get_object_or_404(Author, id=UUID(author_id))
        followers = author.followers.all()
        serialized_followers = [author_to_json(follower) for follower in followers if follower is not None]
        response_data = {"type": "followers", "items": serialized_followers}
        return Response(response_data)


class AuthorFollowingView(APIView):
    @staticmethod
    def get(request, author_id):
        author = get_object_or_404(Author, id=UUID(author_id))
        following = author.following.all()
        serialized_following = [author_to_json(followed) for followed in following if followed is not None]
        response_data = {"type": "following", "items": serialized_following}
        return Response(response_data)


class AuthorFriendsView(APIView):
    @staticmethod
    def get(request, author_id):
        author = get_object_or_404(Author, id=UUID(author_id))
        friends = author.get_friends()
        serialized_friends = [AuthorSerializer(friend).data for friend in friends if friend is not None]
        response_data = {"type": "friends", "items": serialized_friends}
        return Response(response_data,status=status.HTTP_200_OK)
