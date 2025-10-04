from django.shortcuts import render
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    DestroyAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    ListAPIView,
    CreateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit
from habits.paginators import CustomPaginator
from habits.serializers import HabitSerializer, PublicListHabitSerializer


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список личных привычек",
    ),
)
class HabitListAPIView(ListAPIView):
    """
    Получение списка привычек, созданных текущим пользователем. Требуются авторизация.
    Суперпользователь и модератор могут просматривать весь список привычек.
    Реализована пагинация по 5 элементов на странице.
    """

    serializer_class = HabitSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Habit.objects.filter(owner=self.request.user)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список публичных привычек",
    ),
)
class PublicHabitListAPIView(ListAPIView):
    """
    Получение списка публичных привычек. Доступно для всех пользователей.
    Реализована пагинация по 5 элементов на странице.
    """

    serializer_class = PublicListHabitSerializer
    pagination_class = CustomPaginator
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Создание привычки",
    ),
)
class HabitCreateAPIView(CreateAPIView):
    """
    Создание новой привычки. Требуются авторизация.
    Параллельно создается периодическая задача в зависимости от указанной периодичности привычки.
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]


@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        operation_summary="Редактирование привычки",
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="Частичное редактирование привычки",
    ),
)
class HabitUpdateAPIView(UpdateAPIView):
    """
    Редактирование информации о привычке.
    Доступ к конкретным привычкам есть только у создателя привычки, модератора и суперпользователя.
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def perform_update(self, serializer):
        user = self.request.user
        habit = self.get_object()

        if not user == habit.owner:
            raise PermissionDenied("У Вас нет прав редактировать эту привычку.")
        serializer.save()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Просмотр привычки",
    ),
)
class HabitRetrieveAPIView(RetrieveAPIView):
    """
    Просмотр детальной информации о привычке.
    Неавторизованный пользователь может просматривать только публичные привычки.
    Непубличную привычку может просматривать только создатель, модератор и суперпользователь.
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get_object(self):
        obj = super().get_object()

        if not (obj.is_public or obj.owner == self.request.user):
            raise PermissionDenied(
                "У Вас нет прав просматривать информацию об этой привычке."
            )
        return obj


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Удаление привычки",
    ),
)
class HabitDestroyAPIView(DestroyAPIView):
    """
    Владелец привычки может удалять привычку из БД.
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.owner:
            raise PermissionDenied("У вас нет прав на удаление этой привычки.")

        self.perform_destroy(instance)
        return Response(status=204)
