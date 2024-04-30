import logging
import uuid

import requests
from django.contrib.auth.models import User
from django.db import models
from django.db.models import ForeignKey
from requests import Response
from requests.auth import HTTPBasicAuth


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = ForeignKey(User, on_delete=models.CASCADE)
    host = models.URLField(max_length=1024, unique=True)
    enabled = models.BooleanField(default=True)
    our_username = models.CharField(max_length=128, blank=True, null=True)
    our_password = models.CharField(max_length=128, blank=True, null=True)

    def make_url(self, postfix: str) -> str:
        if postfix[0] == "/":
            return f"{self.host}{postfix[1:]}"
        else:
            return f"{self.host}{postfix}"

    def r_get(self, postfix: str, *args, **kwargs) -> Response:
        return requests.get(self.make_url(postfix), auth=(self.our_username, self.our_password), *args, **kwargs)

    def r_post(self, postfix: str, auth=None, *args, **kwargs) -> Response:
    # If auth is provided, add it to the request
        if auth:
            return requests.post(self.make_url(postfix), auth=HTTPBasicAuth(*auth), *args, **kwargs)
        else:
            return requests.post(self.make_url(postfix), *args, **kwargs)

    def r_put(self, postfix: str, *args, **kwargs) -> Response:
        return requests.put(self.make_url(postfix), *args, **kwargs)

    def r_delete(self, postfix: str, *args, **kwargs) -> Response:
        return requests.delete(self.make_url(postfix), *args, **kwargs)
