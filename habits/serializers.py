from rest_framework import serializers

from habits.models import Habit
from habits.validators import CheckHabitValidator, TimeToCompleteValidator, DateDeadlineValidator, PeriodicityValidator


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        validators = [
            CheckHabitValidator(
                associated_habit="associated_habit",
                reward="reward",
                is_enjoyable="is_enjoyable",
            ),
            TimeToCompleteValidator(time_to_complete="time_to_complete"),
            DateDeadlineValidator(date_deadline="date_deadline"),
            PeriodicityValidator(periodicity="periodicity"),
        ]
        extra_kwargs = {"owner": {"read_only": True}}


class PublicListHabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ('id', 'action', 'periodicity', 'time_to_complete', 'is_public')
