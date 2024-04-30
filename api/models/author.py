from __future__ import annotations

import urllib.parse
import uuid
from typing import NewType

import requests
from django.contrib.auth.models import User, AnonymousUser
from django.db import models

from web_dev_noobs_be.settings import SRV_URL
from .node import Node

AuthorID = NewType("AuthorID", uuid.UUID)


class Author(models.Model):
    """
    An author local to the node.
    """

    # the underlying django user connected to an author
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # for remote authors
    extern_id = models.CharField(max_length=1024, null=True, blank=True)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, null=True, blank=True)

    id: AuthorID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    github = models.URLField(blank=True)
    profile_image = models.URLField(blank=True)
    remote_name = models.CharField(max_length=1024,null=True, blank=True)

    # an author is unable to be used until approved
    is_approved = models.BooleanField(default=False)

    following = models.ManyToManyField("self", symmetrical=False, related_name="followers", blank=True)

    @property
    def remote(self) -> bool:
        return self.node is not None

    @property
    def a_name(self) -> str:
        if self.remote:
            return self.remote_name
        elif self.user is not None:
            return self.user.username
        else:
            return "Unknown"

    def is_friend(self, other_user: User | Author) -> bool:
        """
        Checks if both authors are mutually following each other.
        """

        if isinstance(other_user, AnonymousUser):
            return False

        # if it is User only handle local authors
        other_author = other_user if isinstance(other_user, Author) else Author.objects.get(user=other_user)

        if other_author.remote:
            return self.is_followed_by(other_author.id)  # because we can assume requests are accepted
        else:
            return self.is_following(other_author.id) and self.is_followed_by(other_author.id)

    def __str__(self) -> str:
        if self.remote:
            return f"Remote: {self.id}"
        else:
            return f"{self.user.username} [{self.id}]"

    def follow(self, other_user: Author):
        """
        Make this author follow the other user.
        Effects: DB.
        """
        self.following.add(other_user)


    def is_following(self, other_id: AuthorID) -> bool:
        """
        Return whether this author follows the other user with some id
        Effects: DB
        """

        author = Author.objects.get(pk=other_id)
        #not sure if we need this or not
        if author.remote:
            self_id = f"{SRV_URL}/api/authors/{self.id}"
            p_encoded = urllib.parse.quote(self_id)
            r = requests.get(author.node.make_url(f"author/{author.extern_id}/followers/{p_encoded}"))
            return r.status_code == 200
        else:
            return self.following.filter(id=other_id).exists()

    def is_followed_by(self, other_id: AuthorID) -> bool:
        return self.followers.filter(id=other_id).exists()

    def remove_follower(self, sender: Author):
        self.followers.remove(sender)

    def unfollow(self, other_user: Author):
    
        self.following.remove(other_user)

    def get_friends(self):
        """
        Returns a QuerySet of Authors who are mutual followers (i.e., friends).
        """
        following_ids = self.following.values_list('id', flat=True)
        followers_ids = self.followers.values_list('id', flat=True)
        friends_ids = set(following_ids).intersection(set(followers_ids))
        return Author.objects.filter(id__in=friends_ids)