import datetime
import json

import requests
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from config.settings import TELEGRAM_URL, TELEGRAM_BOT_TOKEN


def send_telegram_message(message, chat_id):
    params = {"text": message, "chat_id": chat_id}
    response = requests.get(
        f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage", params=params
    )


def set_schedule_every_day(habit_id, periodicity):

    schedule, created = IntervalSchedule.objects.get_or_create(
        periodicity=periodicity,
        period=IntervalSchedule.DAYS,
    )

    PeriodicTask.objects.create(
        interval=schedule,
        name="Habit Reminder Bot",
        task="habits.tasks.send_reminder_with_bot",
        args=json.dumps([habit_id]),
        kwargs=json.dumps({}),
        expires=datetime.utcnow() + datetime.timedelta(days=1),
    )
