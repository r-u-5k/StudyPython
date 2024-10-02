from django.urls import path, include
from .views import (helloAPI, bookAPI, booksAPI, BookAPI, BooksAPI,
                    BooksAPIMixins, BookAPIMixins,
                    BooksAPIGenerics, BookAPIGenerics,
                    BooksAPIViewSet)
from rest_framework.routers import SimpleRouter

# urlpatterns = [
#     path("hello/", helloAPI),
#     path("fbv/books/", booksAPI),
#     path("fbv/book/<int:bid>/", bookAPI),
#     path("cbv/books/", BooksAPI.as_view()),
#     path("cbv/book/<int:bid>/", BookAPI.as_view()),
#     path("mixin/books/", BooksAPIMixins.as_view()),
#     path("mixin/book/<int:bid>/", BookAPIMixins.as_view()),
#     path("generics/books/", BooksAPIGenerics.as_view()),
#     path("generics/book/<int:bid>/", BookAPIGenerics.as_view())
# ]

router = SimpleRouter()
router.register(r'viewset/books', BooksAPIViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
]
