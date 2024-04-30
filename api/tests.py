import base64
import json
import random
import string
import urllib
from uuid import uuid4

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from web_dev_noobs_be.settings import BASE_DIR
from .models import Author, Post, Notification, Like, Node
from .serializers import AuthorSerializer, LikeSerializer


def setup_authors(n: int) -> [Author]:
    authors = []
    for _ in range(n):
        # TODO test on a larger variety of usernames and passwords
        username = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
        user = User.objects.create_user(username, email=f"{username}@example.com", password=f"{username}pwd")
        author = Author.objects.create(user=user, github=f"https://www.github.com/{user.username}",
                                       profile_image=f"https://example.com/{user.username}", is_approved=True, )
        authors.append(author)
    return authors


class AuthorTestCase(TestCase):
    def setUp(self):
        authors: list[Author] = setup_authors(2)
        self.first = authors[0]
        self.second = authors[1]
        self.first.follow(self.second)

    def test_pagination(self):
        large_page_request = json.loads(self.client.get("/api/authors/?size=100&page=1").content)

        single_author_page_response = json.loads(self.client.get("/api/authors/?size=1&page=1").content)

        assert len(large_page_request["items"]) == 2
        assert large_page_request["type"] == "authors"

        assert len(single_author_page_response["items"]) == 1
        assert single_author_page_response["type"] == "authors"

    def test_display_name(self):
        first_response = json.loads(self.client.get(f"/api/authors/{self.first.id}/").content)
        second_response = json.loads(self.client.get(f"/api/authors/{self.second.id}/").content)

        assert first_response["displayName"] == self.first.user.username
        assert second_response["displayName"] == self.second.user.username

    def test_github(self):
        first_response = json.loads(self.client.get(f"/api/authors/{self.first.id}/").content)
        second_response = json.loads(self.client.get(f"/api/authors/{self.second.id}/").content)

        assert first_response["github"] == self.first.github
        assert second_response["github"] == self.second.github

    def test_profile_image(self):
        first_response = json.loads(self.client.get(f"/api/authors/{self.first.id}/").content)
        second_response = json.loads(self.client.get(f"/api/authors/{self.second.id}/").content)

        assert first_response["profileImage"] == self.first.profile_image
        assert second_response["profileImage"] == self.second.profile_image

    def test_follows(self):
        self.assertTrue(self.second.is_followed_by(self.first.id))

        followers_response = json.loads(self.client.get(f"/api/authors/{self.second.id.hex}/followers").content)

        assert followers_response["type"] == "followers"
        assert len(followers_response["items"]) == 1
        assert any(a["id"] == AuthorSerializer(self.first).data["id"] for a in followers_response["items"])


class UpdateAuthorTest(TestCase):
    def setUp(self):
        authors: list[Author] = setup_authors(1)
        self.author = authors[0]

    def test_update_username(self):
        gr = self.client.get(f"/api/authors/{self.author.id}/")
        self.assertEqual(gr.status_code, status.HTTP_200_OK)
        author_data = json.loads(gr.content)
        self.assertNotEquals(author_data["displayName"], "newName")

        ur = self.client.put(f"/api/authors/{self.author.id}/", data={"displayName": "newName"},
                             content_type="application/json", headers={
                "Authorization": make_basic_header(self.author.user.username, self.author.user.username + "pwd")}, )
        self.assertEqual(ur.status_code, status.HTTP_200_OK, "Failed to update author!")

        gr = self.client.get(f"/api/authors/{self.author.id}/")
        self.assertEqual(gr.status_code, status.HTTP_200_OK)
        author_data = json.loads(gr.content)
        self.assertEqual(author_data["displayName"], "newName")

    def test_update_profile_image(self):
        new_profile_image_link = "https://i.imgur.com/k7XVwpB.jpeg"

        gr = self.client.get(f"/api/authors/{self.author.id}/")
        self.assertEqual(gr.status_code, status.HTTP_200_OK)
        author_data = json.loads(gr.content)
        self.assertNotEquals(author_data["profileImage"], new_profile_image_link)

        ur = self.client.put(f"/api/authors/{self.author.id}/", data={"profileImage": new_profile_image_link},
                             content_type="application/json", headers={
                "Authorization": make_basic_header(self.author.user.username, self.author.user.username + "pwd")}, )
        self.assertEqual(ur.status_code, status.HTTP_200_OK, "Failed to update author!")
        gr = self.client.get(f"/api/authors/{self.author.id}/")
        self.assertEqual(gr.status_code, status.HTTP_200_OK)
        author_data = json.loads(gr.content)
        self.assertEqual(author_data["profileImage"], new_profile_image_link)

    def test_update_github(self):
        new_github_link = "https://github.com/gjohnson"

        gr = self.client.get(f"/api/authors/{self.author.id}/")
        self.assertEqual(gr.status_code, status.HTTP_200_OK)
        author_data = json.loads(gr.content)
        self.assertNotEquals(author_data["github"], new_github_link)

        ur = self.client.put(f"/api/authors/{self.author.id}/", data={"github": new_github_link},
                             content_type="application/json", headers={
                "Authorization": make_basic_header(self.author.user.username, self.author.user.username + "pwd"), }, )
        self.assertEqual(ur.status_code, status.HTTP_200_OK, "Failed to update author!")
        gr = self.client.get(f"/api/authors/{self.author.id}/")
        self.assertEqual(gr.status_code, status.HTTP_200_OK)
        author_data = json.loads(gr.content)
        self.assertEqual(author_data["github"], new_github_link)

    def test_update_without_auth(self):
        ur = self.client.put(f"/api/authors/{self.author.id}/", data={"github": "https://github.com/gjohnson"},
                             content_type="application/json", )
        self.assertTrue(400 <= ur.status_code < 500, "Updated author, should not have been updated")
        gr = self.client.get(f"/api/authors/{self.author.id}/")
        self.assertEqual(gr.status_code, status.HTTP_200_OK)
        author_data = json.loads(gr.content)
        self.assertNotEqual(author_data["github"], "https://github.com/gjohnson")

    def test_update_with_bad_auth(self):
        ur = self.client.put(f"/api/authors/{self.author.id}/", data={"github": "https://github.com/gjohnson"},
                             content_type="application/json",
                             headers={"Authorization": make_basic_header("not_valid", "invalid")}, )
        self.assertTrue(400 <= ur.status_code < 500, "Updated author, should not have been updated")
        gr = self.client.get(f"/api/authors/{self.author.id}/")
        self.assertEqual(gr.status_code, status.HTTP_200_OK)
        author_data = json.loads(gr.content)
        self.assertNotEqual(author_data["github"], "https://github.com/gjohnson")


class PostTestCase(TestCase):
    def setUp(self) -> None:
        self.k = 5
        self.authors = setup_authors(self.k)

    def make_intro_post(self, i: int, visibility: Post.Visibility = Post.Visibility.PUBLIC):
        uuid = self.authors[i].id.hex
        username = self.authors[i].user.username
        post_data = {"title": f"{username}'s first post", "contentType": "text/plain",
                     "content": f"Hello I am {username}.", "description": "Intro post", "visibility": visibility.name, }

        basic_header = make_basic_header(username, username + "pwd")
        headers = {"Authorization": basic_header}

        make_post = self.client.post(f"/api/authors/{uuid}/posts/", data=post_data, headers=headers)
        assert make_post.status_code == 200
        return make_post, post_data

    def test_make_post(self):
        """
        Tests making posts and retrieving that post.
        """
        for i in range(self.k):
            make_post, post_data = self.make_intro_post(i)
            assert make_post.data["id"] is not None
            get_post = self.client.get(make_post.data["id"])
            assert get_post.status_code == 200
            post = json.loads(get_post.content)

            post_uuid_hex = post["id"].split("/")[-1]

            expected_url = (f"/api/authors/{self.authors[i].id.hex}/posts/{post_uuid_hex}")

            # all three are true as this is a local author
            assert post["id"].endswith(expected_url)
            assert post["origin"].endswith(expected_url)
            assert post["source"].endswith(expected_url)

            assert post["type"] == "post"

            assert post["title"] == post_data["title"]
            assert post["description"] == post_data["description"]
            self.assertEquals(post["visibility"], post_data["visibility"])
            assert post["content"] == post_data["content"]
            self.assertEquals(post["contentType"], post_data["contentType"])

            author = Author.objects.get(id=self.authors[i].id)

            assert post["author"] == AuthorSerializer(author).data

    def test_image_post(self):
        for i in range(self.k):
            path = (BASE_DIR / "public/logo192.png").resolve()
            with open(path, "rb") as f:
                contents = f.read()
            username = self.authors[i].user.username
            post_data = {"title": f"{username}'s first post", "contentType": "image/png;base64",
                         "content": base64.b64encode(contents).decode("utf-8"), "description": "Intro post",
                         "visibility": "UNLISTED", }
            basic_header = make_basic_header(username, username + "pwd")
            pr = self.client.post(f"/api/authors/{self.authors[i].id.hex}/posts/", data=post_data,
                                  content_type="application/json", headers={"Authorization": basic_header}, )
            self.assertEqual(pr.status_code, status.HTTP_200_OK)
            post_id = json.loads(pr.content)["id"]

            gr = self.client.get(f"{post_id}/image")
            self.assertEqual(gr.status_code, status.HTTP_200_OK)
            self.assertEqual(contents, gr.content)
            self.assertEqual(gr.headers["Content-Type"], "image/png")

    def test_friends_post(self):
        for i in range(self.k):
            author = self.authors[i]

            mp, pd = self.make_intro_post(i, visibility=Post.Visibility.FRIENDS)
            assert mp.status_code == 200

            assert mp.data["id"] is not None

            # request the post without auth
            gp = self.client.get(mp.data["id"])
            self.assertEqual(gp.status_code, 403)

            # request with author's authentication
            username = author.user.username
            basic_header = ("Basic " + base64.b64encode(f"{username}:{username}pwd".encode()).decode())
            gp = self.client.get(mp.data["id"], headers={"Authorization": basic_header})
            assert gp.status_code == 200

            # request with user that is NOT friend [wrap around authors if necessary]
            username = self.authors[(i + 1) % self.k].user.username
            basic_header = ("Basic " + base64.b64encode(f"{username}:{username}pwd".encode()).decode())
            gp = self.client.get(mp.data["id"], headers={"Authorization": basic_header})
            assert gp.status_code == 403

    def test_update_content(self):
        for i in range(self.k):
            mp, pd = self.make_intro_post(i)
            assert mp.status_code == 200
            assert mp.data["id"] is not None

            ud = {"content": "2nd hello, but still first post!", }

            # attempt update without any authentication
            up = self.client.put(mp.data["id"], data=ud, content_type="application/json")
            assert up.status_code == 403
            gp = self.client.get(mp.data["id"])
            assert gp.data == mp.data

            # attempt update as different user
            username = self.authors[(i + 1) % self.k].user.username
            basic_header = ("Basic " + base64.b64encode(f"{username}:{username}pwd".encode()).decode())
            up = self.client.put(mp.data["id"], data=ud, content_type="application/json",
                                 headers={"Authorization": basic_header}, )
            assert up.status_code == 403
            gp = self.client.get(mp.data["id"])
            assert gp.data == mp.data

            # update as original author
            username = self.authors[i].user.username
            basic_header = ("Basic " + base64.b64encode(f"{username}:{username}pwd".encode()).decode())
            up = self.client.put(mp.data["id"], data=ud, content_type="application/json",
                                 headers={"Authorization": basic_header}, )
            assert up.status_code == 200
            gp = self.client.get(mp.data["id"])
            assert gp.data != mp.data
            for s in ["id", "title", "contentType", "description", "visibility", "source", "origin", "published", ]:
                assert gp.data[s] == mp.data[s]
            assert gp.data["content"] == ud["content"]

    def test_delete(self):
        for i in range(self.k):
            mp, pd = self.make_intro_post(i)
            assert mp.status_code == 200
            assert mp.data["id"] is not None

            # attempt deletion without authentication
            dp = self.client.delete(mp.data["id"])
            assert dp.status_code == 403

            # attempt to delete with other user
            username = self.authors[(i + 1) % self.k].user.username
            basic_header = ("Basic " + base64.b64encode(f"{username}:{username}pwd".encode()).decode())
            dp = self.client.delete(mp.data["id"], headers={"Authorization": basic_header})
            assert dp.status_code == 403

            # at this point assure the post still exists and is accurate
            gp = self.client.get(mp.data["id"])
            for s in pd.keys():
                assert gp.data[s] == mp.data[s]

            # delete with author
            username = self.authors[i].user.username
            basic_header = ("Basic " + base64.b64encode(f"{username}:{username}pwd".encode()).decode())
            dp = self.client.delete(mp.data["id"], headers={"Authorization": basic_header})
            assert dp.status_code == 200

            gp = self.client.get(mp.data["id"])
            assert gp.status_code == 404

    def test_top_level_get(self):
        for i in range(self.k):
            mp1, pd1 = self.make_intro_post(i)
            mp2, pd2 = self.make_intro_post(i)
            mp3, pd3 = self.make_intro_post(i, visibility=Post.Visibility.FRIENDS)
            mp4, pd4 = self.make_intro_post(i, visibility=Post.Visibility.UNLISTED)

            assert (
                    mp1.status_code == 200 and mp2.status_code == 200 and mp3.status_code == 200 and mp4.status_code == 200)

            page_size = 1
            for page in range(1, 2 + 1):
                gpage = self.client.get(f"/api/authors/{self.authors[i].id.hex}/posts/?size={page_size}&page={page}")
                self.assertEquals(gpage.status_code, 200)

                gpd = json.loads(gpage.content)
                self.assertEquals(gpd["type"], "posts")
                self.assertEquals(len(gpd["items"]), 1)

            # only 4 pages, so 5th page should fail
            page = 5
            gpage = self.client.get(f"/api/authors/{self.authors[i].id.hex}/posts/?size={page_size}&page={page}")
            self.assertEquals(gpage.status_code, 404)

            page_size = 3
            for page in range(1, 1 + 1):
                gpage = self.client.get(f"/api/authors/{self.authors[i].id.hex}/posts/?size={page_size}&page={page}")
                self.assertEquals(gpage.status_code, 200)

                gpd = json.loads(gpage.content)
                self.assertEquals(gpd["type"], "posts")
                self.assertEquals(len(gpd["items"]), 2 if page == 1 else 1)

            # only 2 pages, so 3rd page should fail
            page = 2
            gpage = self.client.get(f"/api/authors/{self.authors[i].id.hex}/posts/?size={page_size}&page={page}")
            self.assertEquals(gpage.status_code, 404)


# test the notion of friends
class FriendsTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="user1", password="<PASSWORD>", email="fake@example.com")
        self.author1 = Author.objects.create(user=self.user1, github="", profile_image="", is_approved=True)
        self.user2 = User.objects.create(username="user2", password="<PASSWORD>", email="fake2@example.com")
        self.author2 = Author.objects.create(user=self.user2, github="", profile_image="", is_approved=True)

    def test_unidirectional_not_friends(self):
        self.author1.follow(self.author2)
        self.assertFalse(self.author1.is_friend(self.author2.user))
        self.assertFalse(self.author2.is_friend(self.author1.user))

    def test_friends(self):
        self.author1.follow(self.author2)
        self.author2.follow(self.author1)

        self.assertTrue(self.author1.is_following(self.author2.id))
        self.assertTrue(self.author2.is_following(self.author1.id))
        self.assertTrue(self.author1.is_friend(self.author2.user))
        self.assertTrue(self.author2.is_friend(self.author1.user))

        self.assertFalse(self.author1.is_friend(self.author1.user))
        self.assertFalse(self.author2.is_friend(self.author2.user))


def make_basic_header(username, password):
    return "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()


class InboxTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # self.user = User.objects.create_user(username='testuser', password='testpass123')
        # self.author = Author.objects.create(user=self.user)
        self.authors = setup_authors(1)
        self.url = reverse("author_inbox", kwargs={"author_id": self.authors[0].id})

    def test_post_to_inbox(self):
        data = {
            "type": "Follow",
            "content": "content"

        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(f"Notification created successfully and sent to {self.authors[0].user.username}",
                      str(response.data), )

    def test_invalid_type(self):
        data = {"type": "invalid", "content": "This is an invalid post"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertIn("The type can only be post, comment, Like, or Follow", str(response.data))

    def test_get_inbox_with_no_params(self):
        basic_header = ("Basic " + base64.b64encode(
            f"{self.authors[0].user.username}:{self.authors[0].user.username}pwd".encode()).decode())
        response = self.client.get(self.url, headers={"Authorization": basic_header})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_inbox_without_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_inbox_with_authentication(self):
        page = 1
        size = 3
        url_with_params = f"{self.url}?page={page}&size={size}"
        basic_header = ("Basic " + base64.b64encode(
            f"{self.authors[0].user.username}:{self.authors[0].user.username}pwd".encode()).decode())
        response = self.client.get(url_with_params, headers={"Authorization": basic_header}, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_inbox_with_no_item(self):
        basic_header = ("Basic " + base64.b64encode(
            f"{self.authors[0].user.username}:{self.authors[0].user.username}pwd".encode()).decode())
        response = self.client.delete(self.url, headers={"Authorization": basic_header})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("No notification in inbox to clear", str(response.data))

    def test_delete_inbox_with_item(self):
        Notification.objects.create(recipient=self.authors[0], type="comment", data="test comment")
        basic_header = make_basic_header(self.authors[0].user.username, self.authors[0].user.username + "pwd")
        response = self.client.delete(self.url, headers={"Authorization": basic_header})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Inbox Cleared", str(response.data))


class GetAuthorLikesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.authors = setup_authors(1)
        self.like = Like.objects.create(object_id=str(uuid4()), author=self.authors[0], object_type="post")
        self.url = reverse('author-liked', kwargs={'author_id': self.authors[0].id})
        self.basic_header = ("Basic " + base64.b64encode(
            f"{self.authors[0].user.username}:{self.authors[0].user.username}pwd".encode()).decode())

    def test_get_likes_for_author(self):
        response = self.client.get(self.url, headers={"Authorization": self.basic_header}, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['type'], 'Liked')
        expected_item = LikeSerializer(self.like).data
        self.assertEqual(response.data['items'][0], expected_item)


class LikePostViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.authors = setup_authors(1)
        self.post = Post.objects.create(title="Sample Post", description="testing the view", content="Testing the post",
                                        author=self.authors[0], visibility=Post.Visibility.PUBLIC,
                                        content_type=Post.ContentType.PLAIN)
        self.like = Like.objects.create(object_id=self.post.uuid, author=self.authors[0], object_type="post")
        self.url = reverse('post-likes', kwargs={'author_id': self.authors[0].id, 'post_id': self.post.uuid})

    def test_get_likes_for_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        response_data = json.loads(response.content)

        likes = Like.objects.filter(object_id=self.post.uuid, object_type="post")
        
        expected_data = LikeSerializer(likes, many=True).data
        self.assertEqual(response_data["items"], expected_data)


class ForeignFollowerTestCase(TestCase):
    def setUp(self) -> None:

        self.external_id = "random_id"
        self.node_admin = User.objects.create_user("node", password="admin")
        self.node = Node.objects.create(host="https://wwww.example.com/srv/", user=self.node_admin)
        self.external = self.node.host + "authors/" + self.external_id

        self.user = User.objects.create_user("user", password="password")
        self.author = Author.objects.create(user=self.user, is_approved=True)
        self.bh = make_basic_header("user", "password")

    def test_follow_no_auth(self) -> None:
        self.external_author = Author.objects.create(extern_id=self.external_id, node=self.node, is_approved=True)
        pr = self.client.put(f"/api/authors/{self.author.id.hex}/followers/{urllib.parse.quote(self.external)}")
        self.assertEqual(pr.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.author.is_followed_by(self.external_author.id))

    def test_follow(self) -> None:
        self.external_author = Author.objects.create(extern_id=self.external_id, node=self.node, is_approved=True)
        pr = self.client.put(f"/api/authors/{self.author.id.hex}/followers/{urllib.parse.quote(self.external)}",
                             headers={"Authorization": self.bh})
        self.assertEqual(pr.status_code, status.HTTP_200_OK)
        self.assertTrue(self.author.is_followed_by(self.external_author.id))

    # def test_delete_follow_no_auth(self) -> None:
    #     ForeignFollowerTestCase.test_follow(self)
    #     dr = self.client.delete(f"/api/authors/{self.author.id.hex}/followers/{urllib.parse.quote(self.external)}")
    #     self.assertEqual(dr.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertTrue(self.author.is_followed_by(self.external_author.id))

    # def test_delete_follow(self) -> None:
    #     ForeignFollowerTestCase.test_follow(self)
    #     dr = self.client.delete(f"/api/authors/{self.author.id.hex}/followers/{urllib.parse.quote(self.external)}",
    #                             headers={"Authorization": self.bh})
    #     self.assertEqual(dr.status_code, status.HTTP_200_OK)
    #     self.assertFalse(self.author.is_followed_by(self.external_author.id))

    # def test_get_follow(self) -> None:
    #     gr = self.client.get(f"/api/authors/{self.author.id}/followers/{urllib.parse.quote(self.external)}")
    #     self.assertEqual(gr.status_code, status.HTTP_404_NOT_FOUND)

    #     ForeignFollowerTestCase.test_follow(self)
    #     gr = self.client.get(f"/api/authors/{self.author.id}/followers/{urllib.parse.quote(self.external)}")
    #     self.assertEqual(gr.status_code, status.HTTP_200_OK)

    #     self.client.delete(f"/api/authors/{self.author.id.hex}/followers/{urllib.parse.quote(self.external)}",
    #                        headers={"Authorization": self.bh})
    #     gr = self.client.get(f"/api/authors/{self.author.id}/followers/{urllib.parse.quote(self.external)}")
    #     self.assertEqual(gr.status_code, status.HTTP_404_NOT_FOUND)
