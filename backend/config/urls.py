from django.contrib import admin
from django.urls import include, path
from books.views import AskAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("books.urls")),
    path("api/ask/", AskAPIView.as_view(), name="ask"),
]
