from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from fe import views as fev


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/ext/", include("ext.urls")),
    path("authentication/", include("authentication.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="AuthCord API Documentation",
    ),
    re_path(".*", fev.index),
]
