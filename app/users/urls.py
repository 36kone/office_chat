from django.urls import path

from app.users.views.users_views import UserCreateView, UserDetailView, UserSearchView

urlpatterns = [
    path("users/", UserCreateView.as_view()),
    path("users/search/", UserSearchView.as_view()),
    path("users/<uuid:user_id>/", UserDetailView.as_view()),
]
