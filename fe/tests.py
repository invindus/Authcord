from django.test import TestCase


class FrontendTestCase(TestCase):
    def test_index(self):
        r = self.client.get("/")
        self.assertEqual(r["Content-Type"], "text/html")
        self.assertEqual(r.status_code, 200)
