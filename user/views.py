from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import DestroyAPIView, UpdateAPIView, RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.models import User
from user.serializers import UserRegisterSerializer, UserPublicSerializer, UserSerializers


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Создание пользователя",
        operation_description="Создание нового пользователя. Для авторизации требуются email и пароль.",
    ),
)
class UserCreateAPIView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список пользователей",
        operation_description="Вывод списка авторизованных пользователей. Требуется авторизация. Для просмотра доступны "
        "поля: email, имя, город, аватар.",
        responses={200: UserPublicSerializer(many=True)},
    ),
)
class UserListAPIView(ListAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()


class UserRetrieveAPIView(LoginRequiredMixin, RetrieveAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        else:
            raise PermissionDenied


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserSerializers
    queryset = User.objects.all()


class UserDestroyAPIView(DestroyAPIView):
    queryset = User.objects.all()


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
