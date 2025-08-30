from django.db import models

from user.models import User


class Habit(models.Model):

    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, verbose_name="Автор", null=True, blank=True
    )
    location = models.CharField(
        max_length=30,
        verbose_name="Место",
        help_text="Место, в котором необходимо выполнять привычку",
        null=True,
        blank=True,
    )
    date_deadline = models.DateField(
        verbose_name="Дата выполнения привычки",
        help_text="Дата, когда необходимо выполнять привычку",
        null=True,
        blank=True,
    )
    time_deadline = models.TimeField(
        verbose_name="Время выполнения привычки",
        help_text="Время, когда необходимо выполнять привычку",
        null=True,
        blank=True,
    )
    action = models.CharField(
        max_length=50,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычка",
    )
    is_enjoyable = models.BooleanField(
        verbose_name="Признак приятной привычки",
        help_text="Привычка, способ вознаградить себя за выполнение полезной привычки",
        null=True,
        blank=True,
    )
    associated_habit = models.ForeignKey(
        "Habit",
        on_delete=models.CASCADE,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой, важно указывать для полезных привычек, но не для "
        "приятных",
        null=True,
        blank=True,
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность",
        help_text="Периодичность выполнения привычки для напоминания в днях",
    )
    reward = models.CharField(
        max_length=50,
        verbose_name="Вознаграждение",
        help_text="Вознаграждение за выполнение привычки",
        null=True,
        blank=True,
    )
    time_to_complete = models.PositiveIntegerField(
        verbose_name="Время на выполнение",
        help_text="Время, которое предположительно нужно потратить на выполнение привычки. Укажите в минутах",
        null=True,
        blank=True,
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="Привычки можно публиковать в общий доступ, чтобы другие пользователи могли брать в пример Ваши "
        "привычки",
    )
    is_active = models.BooleanField(verbose_name="Признак активности", default=True)

    def __str__(self):
        return f"Я буду {self.action} в {self.time_deadline} в {self.location}."

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
