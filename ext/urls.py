from django.urls import path

from . import views

urlpatterns = [
    path("post_count", views.post_count, name="post-count"),
    path("authors/<author_id>/post_count", views.author_post_count, name="author-post-count"),
    path("authors/<author_id>/github_activity", views.GetGithubActivity.as_view()),
    path("requests/<path:foreign_id>", views.RequestsView.as_view()),
    path("remote_authors_scan", views.RemoteAuthorsScan.as_view(), name="remote-authors-scan"),
    path("posts/", views.GlobalPostsView.as_view()),
    path("authors/<author_id>/followers", views.AuthorFollowersView.as_view(), name='author-followers'),
    path("authors/<author_id>/following", views.AuthorFollowingView.as_view(), name='author-following'),
    path("authors/<author_id>/friends", views.AuthorFriendsView.as_view(), name='author-friends'),
    path("comments/<path:foreign_id>", views.comments, name="comments"),
]
