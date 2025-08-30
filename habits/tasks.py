from datetime import timezone

from celery import shared_task


from habits.models import Habit
from habits.services import send_telegram_message


@shared_task
def send_reminder_with_bot(habit_id, messagge):
    """ Отправка напоминания о привычке с помощью телеграм-бота. """
    today = timezone.now().today()
    habit = Habit.objects.filter(id=habit_id, time_deadline=today)

    if habit.owner.chat_id:
        send_telegram_message(
            "Напоминание: Сегодня я буду {self.action} в {self.time_deadline} в {self.location}.",
            habit.owner.chat_id
        )
