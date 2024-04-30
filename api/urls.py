from django.urls import path

from ext import views as ext
from . import views

urlpatterns = [
    path("authors/", views.get_all_authors_paginated),
    path("authors/<author_id>/", views.SingleAuthorView.as_view()),
    path("authors/<author_id>/followers", views.FollowersView.as_view()),
    path("authors/<author_id>/followers/<path:foreign_id>", views.ForeignFollowerView.as_view()),
    path("authors/<author_id>/posts/", views.MainPostsView.as_view()),
    path("authors/<author_id>/posts/<post_id>", views.PostView.as_view()),
    path("authors/<author_id>/posts/<post_id>/image", views.image_post_view),
    path(
        "authors/<author_id>/posts/<post_id>/comments",
        views.CommentList.as_view(),
        name="comment-list",
    ),
    path(
        "authors/<author_id>/liked",
        views.GetAuthorLikedAPIView.as_view(),
        name="author-liked",
    ),
    path(
        "authors/<author_id>/posts/<post_id>/likes",
        views.LikePostView.as_view(),
        name="post-likes",
    ),
    path(
        "authors/<author_id>/posts/<post_id>/comments/<comment_id>/likes",
        views.LikeCommentView.as_view(),
        name="comment-likes",
    ),
    path("authors/<author_id>/inbox", views.InboxView.as_view(), name="author_inbox"),

    # Para-Spec
    # Endpoints that *may* be useful to have under /api/ directly, but
    # that don't have a clear reason to exist according to the spec.
    # Main reason is to offer a compromise between /api/ and /api/ext/
    # so that other nodes may be able to use these endpoints.
    path("posts/", ext.GlobalPostsView.as_view()),
]
