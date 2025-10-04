from datetime import date

from rest_framework.exceptions import ValidationError


class CheckHabitValidator:
    """
    Исключение одновременного выбора связанной привычки и указания вознаграждения.
    В связанные привычки могут попадать только привычки с признаком приятной привычки.
    У приятной привычки не может быть вознаграждения или связанной привычки.
    """

    def __init__(self, associated_habit, reward, is_enjoyable):
        self.associated_habit = associated_habit
        self.reward = reward
        self.is_enjoyable = is_enjoyable

    def __call__(self, attrs):
        associated_habit = attrs.get(self.associated_habit)
        reward = attrs.get(self.reward)
        is_enjoyable = attrs.get(self.is_enjoyable)

        if associated_habit and reward:
            raise ValidationError(
                "Не должно быть заполнено одновременно и поле вознаграждения, и поле "
                "связанной привычки. Можно заполнить только одно из двух полей."
            )
        if associated_habit and not associated_habit.is_enjoyable:
            raise ValidationError(
                "В связанные привычки могут попадать только привычки с признаком приятной привычки."
            )
        if is_enjoyable:
            if reward:
                raise ValidationError(
                    "У приятной привычки не может быть вознаграждения."
                )
            if associated_habit:
                raise ValidationError(
                    "У приятной привычки не может быть связанной привычки."
                )
        # return True


class TimeToCompleteValidator:
    """Проверка времени на выполнение привычки."""

    def __init__(self, time_to_complete):
        self.time_to_complete = time_to_complete

    def __call__(self, attrs):
        time_to_complete = attrs.get(self.time_to_complete)

        if not time_to_complete:
            return True

        if int(time_to_complete) > 2:
            raise ValidationError("Время выполнения должно быть не больше 2 минут.")
        # return True


class DateDeadlineValidator:
    """Проверка даты на актуальность."""

    def __init__(self, date_deadline):
        self.date_deadline = date_deadline

    def __call__(self, attrs):
        date_deadline = attrs.get(self.date_deadline)

        today = date.today()

        if date_deadline and date_deadline < today:
            raise ValidationError("Привычка не может быть выполнена задним числом.")

        # return True


class PeriodicityValidator:
    """Проверка периодичности выполнения привычки."""

    def __init__(self, periodicity):
        self.periodicity = periodicity

    def __call__(self, attrs):
        periodicity = attrs.get(self.periodicity)

        if not periodicity:
            return True

        if int(periodicity) > 7:
            raise ValidationError("Нельзя не выполнять привычку более 7 дней")
        # return True
