from django.urls import path

from habits.apps import HabitsConfig
from habits.views import PublicHabitListAPIView, HabitListAPIView, HabitCreateAPIView, HabitUpdateAPIView, \
    HabitDestroyAPIView, HabitRetrieveAPIView

app_name = HabitsConfig.name

urlpatterns = [
    path("public/", PublicHabitListAPIView.as_view(), name="public_habits_list"),
    path("my/", HabitListAPIView.as_view(), name="habits_list"),
    path("create/", HabitCreateAPIView.as_view(), name="habit_create"),
    path("<int:pk>/update/", HabitUpdateAPIView.as_view(), name="habit_update"),
    path("<int:pk>/detail/", HabitRetrieveAPIView.as_view(), name="habit_detail"),
    path("<int:pk>/delete/", HabitDestroyAPIView.as_view(), name="habit_delete"),
]