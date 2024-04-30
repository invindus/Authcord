from django.http import HttpResponse

from web_dev_noobs_be.settings import REACT_BUILD


def index(request):
    with open(REACT_BUILD / "index.html") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/html")

