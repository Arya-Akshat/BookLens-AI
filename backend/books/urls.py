from django.urls import path

from .views import (
    BookDetailAPIView,
    BookListAPIView,
    BookRecommendAPIView,
    BookUploadAPIView,
)

urlpatterns = [
    path("books/", BookListAPIView.as_view(), name="book-list"),
    path("books/upload/", BookUploadAPIView.as_view(), name="book-upload"),
    path("books/<int:pk>/", BookDetailAPIView.as_view(), name="book-detail"),
    path("books/recommend/<int:pk>/", BookRecommendAPIView.as_view(), name="book-recommend"),
]
