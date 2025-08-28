from django.shortcuts import render
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import DestroyAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView, CreateAPIView
from rest_framework.response import Response

from habits.models import Habit


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

    # serializer_class = HabitSerializer
    # pagination_class = CustomPaginator

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Habit.objects.all()

        if not user.is_authenticated:
            raise PermissionDenied("Требуется авторизация.")

        return Habit.objects.filter(owner=self.request.user, is_active=True)


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

    # serializer_class = HabitSerializer
    # pagination_class = CustomPaginator
    # permission_classes = (AllowAny,)

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
    # serializer_class = HabitSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Требуется авторизация для создания привычки.")
        habit = serializer.save()
        habit.owner = self.request.user
        habit.save()

        # if 'Каждые' in habit.periodicity or 'Еже' in habit.periodicity:
        #     set_schedule_every_day(habit.id, habit.periodicity)
        # elif 'раза' in habit.periodicity:
        #     set_schedule_a_few_time(habit.id, habit.periodicity)
        # elif 'По' in habit.periodicity:
        #     set_schedule_every_weekday(habit.id, habit.periodicity)


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
    # serializer_class = HabitSerializer

    def perform_update(self, serializer):
        user = self.request.user
        habit = self.get_object()

        if not (user == habit.owner or user.is_staff or user.is_superuser):
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
    # serializer_class = HabitSerializer

    def get_object(self):
        obj = super().get_object()

        if not (obj.is_public or
                obj.owner == self.request.user or
                self.request.user.is_staff or
                self.request.user.is_superuser):
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
    Суперпользователь может удалять привычку из БД. Обычный пользователь может только изменить статус активности.
    """

    queryset = Habit.objects.all()
    # serializer_class = HabitSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.is_superuser:
            instance.delete()
            return Response(status=204)

        elif request.user != instance.owner:
            raise PermissionDenied("У вас нет прав на удаление этой привычки.")

        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response(status=204)
