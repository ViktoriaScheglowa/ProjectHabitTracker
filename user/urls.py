from django.urls import path

from user.apps import UserConfig
from user.views import UserListAPIView, UserCreateAPIView, UserRetrieveAPIView, UserUpdateAPIView, UserDestroyAPIView

app_name = UserConfig.name


urlpatterns = ([
    path("", UserListAPIView.as_view(), name="user-list"),
    path("create/", UserCreateAPIView.as_view(), name="user-create"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-detail"),
    path("<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    ])
