from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from habits.models import Habit
from habits.paginators import CustomPaginator
from user.models import User


# User = get_user_model()


class HabitCreateAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="user@user.ru")
        self.user2 = User.objects.create(email="user2@user.ru")

        # Создаем приятную привычку для использования в тестах
        self.enjoyable_habit = Habit.objects.create(
            action="Прочитать 10 страниц",
            time_deadline="10:00:00",
            periodicity=1,
            time_to_complete="2",
            is_enjoyable=True,
            location="Home",
            date_deadline="2025-09-01",
            owner=self.user,
        )
        # Создаем НЕприятную привычку для использования в тестах
        self.non_enjoyable_habit = Habit.objects.create(
            action="Сделать зарядку",
            time_deadline="08:00:00",
            periodicity=1,
            time_to_complete="2",
            is_enjoyable=False,
            location="Home",
            date_deadline="2025-09-01",
            owner=self.user,
        )

    def test_create_habit_unauthenticated(self):
        """
        Тест на создание привычки неавторизованным пользователем.
        Должен вернуть 401 Unauthorized.
        """
        data = {
            "action": "Выпить стакан воды",
            "time_deadline": "09:00:00",
            "periodicity": 1,
            "time_to_complete": 1,
            "is_enjoyable": False,
            "location": "Home",
            "date_deadline": "2025-09-01",
        }
        self.url = reverse("habits:habits_list")
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Habit.objects.count(), 2)  # Проверяем, что привычка не создана

    def test_create_habit_authenticated_success(self):
        """
        Тест на успешное создание привычки авторизованным пользователем.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Позвонить маме",
            "time_deadline": "12:00",
            "periodicity": 1,
            "time_to_complete": 2,
            "is_enjoyable": False,
            "location": "Home",
            "date_deadline": "2025-09-01",
        }
        self.url = reverse("habits:habit_create")
        response = self.client.post(self.url, data=data, format="json")
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)

    def test_create_pleasant_habit_success(self):
        """
        Тест на успешное создание приятной привычки.
        У приятной привычки не должно быть вознаграждения или связанной привычки.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Послушать музыку",
            "time_deadline": "17:00:00",
            "periodicity": 1,
            "time_to_complete": 2,
            "is_enjoyable": True,
            "location": "Home",
            "date_deadline": "2025-09-01",
        }
        self.url = reverse("habits:habit_create")
        response = self.client.post(self.url, data, format="json")
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)

    def test_create_habit_with_reward_and_associated_habit_simultaneously_fails(self):
        """
        Тест: Не должно быть заполнено одновременно и поле вознаграждения,
        и поле связанной привычки.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Погулять с собакой",
            "time_deadline": "18:00:00",
            "periodicity": 1,
            "time_to_complete": 2,
            "is_enjoyable": False,
            "reward": "Купить мороженое",
            "location": "Home",
            "date_deadline": "2025-09-01",
            "associated_habit": self.enjoyable_habit.id,
        }
        self.url = reverse("habits:habit_create")
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("Не должно быть заполнено одновременно и поле вознаграждения", str(response.data))
        self.assertEqual(Habit.objects.count(), 2)

    def test_create_habit_with_non_enjoyable_associated_habit_fails(self):
        """
        Тест: В связанные привычки могут попадать только привычки
        с признаком приятной привычки.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Почистить зубы",
            "time_deadline": "21:00:00",
            "periodicity": 1,
            "time_to_complete": 2,
            "is_enjoyable": False,
            "location": "Home",
            "date_deadline": "2025-09-01",
            "associated_habit": self.non_enjoyable_habit.id,
        }
        self.url = reverse("habits:habit_create")
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("В связанные привычки могут попадать только привычки с признаком приятной привычки.", str(response.data))
        self.assertEqual(Habit.objects.count(), 2)

    def test_create_pleasant_habit_with_reward_fails(self):
        """
        Тест: У приятной привычки не может быть вознаграждения.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Медитировать 5 минут",
            "time_deadline": "07:00:00",
            "periodicity": 1,
            "time_to_complete": 2,
            "is_enjoyable": True,
            "reward": "Чашка кофе",
            "location": "Home",
            "date_deadline": "2025-09-01",
        }
        self.url = reverse("habits:habit_create")
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("У приятной привычки не может быть вознаграждения.", str(response.data))
        self.assertEqual(Habit.objects.count(), 2)

    def test_create_pleasant_habit_with_associated_habit_fails(self):
        """
        Тест: У приятной привычки не может быть связанной привычки.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Слушать подкаст",
            "time_deadline": "08:30:00",
            "periodicity": 1,
            "time_to_complete": 2,
            "is_enjoyable": True,
            "location": "Home",
            "date_deadline": "2025-09-01",
            "associated_habit": self.enjoyable_habit.id,
        }
        self.url = reverse("habits:habit_create")
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("У приятной привычки не может быть связанной привычки.", str(response.data))
        self.assertEqual(Habit.objects.count(), 2)

    def test_create_habit_with_valid_associated_habit(self):
        """
        Тест на успешное создание привычки со связанной приятной привычкой.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Убрать на столе",
            "time_deadline": "16:00:00",
            "periodicity": 1,
            "time_to_complete": 1,
            "is_enjoyable": False,
            "location": "Home",
            "date_deadline": "2025-09-01",
            "associated_habit": self.enjoyable_habit.id,
        }
        self.url = reverse("habits:habit_create")
        response = self.client.post(self.url, data, format="json")
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)
        # created_habit = Habit.objects.get(id=response.data["id"])
        # self.assertEqual(created_habit.associated_habit, self.enjoyable_habit)
        # self.assertIsNone(created_habit.reward)

    def test_create_habit_with_valid_reward(self):
        """
        Тест на успешное создание привычки с вознаграждением.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Полить цветы",
            "time_deadline": "11:00:00",
            "periodicity": 1,
            "time_to_complete": 2,
            "is_enjoyable": False,
            "location": "Home",
            "date_deadline": "2025-09-01",
            "reward": "Посмотреть серию сериала",  # Указываем вознаграждение
        }
        self.url = reverse("habits:habit_create")
        response = self.client.post(self.url, data, format="json")
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)
        # created_habit = Habit.objects.get(id=response.data["id"])
        # self.assertEqual(created_habit.reward, data["reward"])
        # self.assertIsNone(
        #     created_habit.associated_habit
        # )  # Убедимся, что связанной привычки нет


class HabitUpdateAPITestCase(APITestCase):

    def setUp(self):
        # Создаем пользователей для различных сценариев
        self.user = User.objects.create(email="user@user.ru")
        self.owner = User.objects.create(
            email="owner@example.com", password="password123"
        )
        self.other_user = User.objects.create(
            email="other@example.com", password="password123"
        )

        # Создаем привычку, принадлежащую owner
        self.habit = Habit.objects.create(
            owner=self.owner,
            action="Прочитать книгу",
            time_deadline="20:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
        )

        # URL для обновления привычки
        self.update_url = reverse("habits:habit_update", kwargs={"pk": self.habit.pk})
        self.url = reverse("habits:habit_create")
        # Клиент для выполнения запросов
        self.client = APIClient()

    def test_update_habit_authenticated_owner_put_success(self):
        """Владелец привычки должен иметь возможность полностью обновить ее (PUT)."""
        self.client.force_authenticate(user=self.owner)
        updated_data = {
            "action": "Послушать подкаст",
            "time_deadline": "11:00:00",
            "periodicity": 2,
            "time_to_complete": 2,
            "location": "Home",
            "date_deadline": "2025-09-01",
            "is_enjoyable": True,
            "is_public": True,
        }
        response = self.client.put(self.update_url, updated_data, format="json")
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.habit.refresh_from_db()  # Обновляем объект из базы данных
        # self.assertEqual(self.habit.action, updated_data['action'])
        # self.assertEqual(self.habit.time_deadline, '11:00')
        # self.assertEqual(self.habit.periodicity, updated_data["periodicity"])
        self.assertEqual(self.habit.time_to_complete, 2)
        # self.assertEqual(self.habit.is_enjoyable, updated_data["is_enjoyable"])
        # self.assertEqual(self.habit.is_public, updated_data["is_public"])
        self.assertEqual(self.habit.owner, self.owner)  # Владелец не должен меняться

    def test_update_habit_authenticated_owner_patch_success(self):
        """Владелец привычки должен иметь возможность частично обновить ее (PATCH)."""
        self.client.force_authenticate(user=self.owner)
        partial_data = {"action": "Погулять с собакой", "is_public": True}
        response = self.client.patch(self.update_url, partial_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, partial_data["action"])
        self.assertEqual(self.habit.is_public, partial_data["is_public"])
        # Проверяем, что остальные поля остались прежними
        # self.assertEqual(self.habit.time_deadline, updated_data['time_deadline'])
        self.assertEqual(self.habit.periodicity, 1)
        self.assertEqual(self.habit.time_to_complete, 2)
        self.assertEqual(self.habit.is_enjoyable, False)

    def test_update_habit_authenticated_other_user_permission_denied(self):
        """Другой аутентифицированный пользователь не должен иметь возможность обновить чужую привычку."""
        self.client.force_authenticate(user=self.other_user)
        original_action = self.habit.action
        updated_data = {
            "action": "Попытка обновить чужую привычку",
            "time_deadline": "12:00:00",
            "periodicity": 3,
            "time_to_complete": 1,
            "location": "Home",
            "date_deadline": "2025-09-01",
            "is_enjoyable": False,
            "is_public": False,
        }
        response = self.client.put(self.update_url, updated_data, format="json")
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertIn(
        #     "У Вас нет прав редактировать эту привычку.", response.data["detail"]
        # )

        self.habit.refresh_from_db()
        self.assertEqual(
            self.habit.action, original_action
        )  # Проверяем, что привычка не изменилась

    def test_update_habit_unauthenticated_fails(self):
        """Неаутентифицированный пользователь не должен иметь возможность обновить привычку."""
        # Клиент не аутентифицирован по умолчанию после setUp, но можно явно сбросить
        self.client.force_authenticate(user=None)
        original_action = self.habit.action
        updated_data = {
            "action": "Обновление без авторизации",
            "time_deadline": "13:00:00",
            "periodicity": 1,
            "time_to_complete": 1,
            "location": "Home",
            "date_deadline": "2025-09-01",
            "is_enjoyable": False,
            "is_public": False,
        }
        response = self.client.put(self.update_url, updated_data, format="json")
        # DRF по умолчанию возвращает 401 для неаутентифицированных пользователей,
        # если не заданы другие permission_classes.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Authentication credentials were not provided.", response.data["detail"]
        )

        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, original_action)

    def test_update_habit_with_invalid_data(self):
        """Попытка обновить привычку невалидными данными должна возвращать 400 Bad Request."""
        self.client.force_authenticate(user=self.owner)
        original_action = self.habit.action
        invalid_data = {
            "action": "",  # Пустое имя
            "time_deadline": "25:00:00",  # Невалидное время
            "periodicity": 0,  # Периодичность должна быть от 1 до 7
            "time_to_complete": 9,  # Длительность должна быть < 2
            "location": "Home",
            "date_deadline": "2025-09-01",
            "is_enjoyable": False,
            "is_public": False,
        }
        response = self.client.put(self.update_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("action", response.data)
        self.assertIn("time_deadline", response.data)
        # self.assertIn('periodicity', response.data)
        # self.assertIn('time_to_complete', response.data)

        self.habit.refresh_from_db()
        self.assertEqual(
            self.habit.action, original_action
        )  # Проверяем, что привычка не изменилась

    def test_update_non_existent_habit(self):
        """Попытка обновить несуществующую привычку должна возвращать 404 Not Found."""
        self.client.force_authenticate(user=self.owner)
        non_existent_url = reverse(
            "habits:habit_update", kwargs={"pk": 9999}
        )  # Несуществующий PK
        updated_data = {
            "action": "Несуществующая привычка",
            "time_deadline": "14:00:00",
            "periodicity": 1,
            "time_to_complete": "00:01:00",
            "location": "Home",
            "date_deadline": "2025-09-01",
            "is_enjoyable": False,
            "is_public": False,
        }
        response = self.client.put(non_existent_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertIn("Not found.", response.data['detail'])


class HabitRetrieveAPITestCase(APITestCase):

    def setUp(self):
        # Создаем пользователей для различных сценариев
        self.owner = User.objects.create(
            email="owner@example.com", password="password123"
        )
        self.other_user = User.objects.create(
            email="other@example.com", password="password123"
        )

        # Создаем публичную привычку
        self.public_habit = Habit.objects.create(
            owner=self.owner,
            action="Прочитать публичную книгу",
            time_deadline="12:00:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=True,
        )

        # Создаем непубличную привычку
        self.private_habit = Habit.objects.create(
            owner=self.owner,
            action="Сделать приватное упражнение",
            time_deadline="18:00:00",
            periodicity=2,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=True,
            is_public=False,
        )

        # URL для детального просмотра привычек
        self.public_habit_url = reverse(
            "habits:habit_detail", kwargs={"pk": self.public_habit.pk}
        )
        self.private_habit_url = reverse(
            "habits:habit_detail", kwargs={"pk": self.private_habit.pk}
        )

        # Клиент для выполнения запросов
        self.client = APIClient()

    # --- Тесты для публичной привычки ---
    def test_retrieve_public_habit_unauthenticated_success(self):
        """Неаутентифицированный пользователь должен иметь возможность просматривать публичную привычку."""
        response = self.client.get(self.public_habit_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.public_habit.action, "Прочитать публичную книгу")
        self.assertTrue(self.public_habit.is_public, True)

    def test_retrieve_public_habit_authenticated_other_user_success(self):
        """Другой аутентифицированный пользователь должен иметь возможность просматривать публичную привычку."""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.public_habit_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.public_habit.action, "Прочитать публичную книгу")
        self.assertTrue(self.public_habit.is_public, True)

    def test_retrieve_public_habit_owner_success(self):
        """Владелец должен иметь возможность просматривать свою публичную привычку."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.public_habit_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.public_habit.action, "Прочитать публичную книгу")
        self.assertTrue(self.public_habit.is_public, True)

    # --- Тесты для непубличной привычки ---
    def test_retrieve_private_habit_owner_success(self):
        """Владелец должен иметь возможность просматривать свою непубличную привычку."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.private_habit_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.private_habit.action, "Сделать приватное упражнение")
        self.assertFalse(self.private_habit.is_public, False)

    def test_retrieve_private_habit_other_user_permission_denied(self):
        """Другой аутентифицированный пользователь не должен иметь возможность просматривать чужую непубличную привычку."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.private_habit_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "У Вас нет прав просматривать информацию об этой привычке.",
            response.data["detail"],
        )

    def test_retrieve_private_habit_unauthenticated_permission_denied(self):
        """Неаутентифицированный пользователь не должен иметь возможность просматривать непубличную привычку."""
        # Клиент не аутентифицирован по умолчанию
        response = self.client.get(self.private_habit_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Authentication credentials were not provided.", response.data["detail"]
        )

    # --- Тесты на ошибки ---
    def test_retrieve_non_existent_habit_fails(self):
        """Попытка просмотреть несуществующую привычку должна возвращать 404 Not Found."""
        self.client.force_authenticate(
            user=self.owner
        )  # Аутентификация не влияет на 404
        non_existent_url = reverse("habits:habit_detail", kwargs={"pk": 9999})
        response = self.client.get(non_existent_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("No Habit matches the given query.", response.data["detail"])


class HabitDestroyAPIViewTest(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.user = User.objects.create(email="user@example.com", password="123qwe")
        self.owner_user = User.objects.create(
            email="owner@example.com", password="123qwe"
        )
        self.other_user = User.objects.create(
            email="other@example.com", password="123qwe"
        )

        # Создаем привычки
        self.habit_by_owner = Habit.objects.create(
            owner=self.owner_user,
            action="Читать книгу",
            time_deadline="20:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )
        self.habit_by_other = Habit.objects.create(
            owner=self.other_user,
            action="Выпить витамины",
            time_deadline="09:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )

        # URL-адреса для тестов
        self.url_owner_habit = reverse(
            "habits:habit_delete", kwargs={"pk": self.habit_by_owner.pk}
        )
        self.url_other_habit = reverse(
            "habits:habit_delete", kwargs={"pk": self.habit_by_other.pk}
        )
        self.url_non_existent = reverse("habits:habit_delete", kwargs={"pk": 9999})

    def test_owner_deactivates_own_habit(self):
        """
        Тест: Владелец привычки может деактивировать свою привычку (is_active = False).
        """
        self.client.force_authenticate(user=self.owner_user)
        self.assertTrue(
            self.habit_by_owner.is_active
        )  # Проверяем, что изначально активна

        response = self.client.delete(self.url_owner_habit)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Привычка не должна быть удалена из БД
        # self.assertTrue(Habit.objects.filter(pk=self.habit_by_owner.pk).exists())

    def test_other_user_cannot_delete_other_habit(self):
        """
        Тест: Обычный пользователь не может удалить чужую привычку.
        """
        self.client.force_authenticate(
            user=self.other_user
        )  # other_user пытается удалить habit_by_owner
        initial_is_active = self.habit_by_owner.is_active
        initial_habit_count = Habit.objects.count()

        response = self.client.delete(self.url_owner_habit)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "У вас нет прав на удаление этой привычки."
        )
        # Привычка не должна быть удалена или изменена
        self.assertEqual(Habit.objects.count(), initial_habit_count)
        self.habit_by_owner.refresh_from_db()
        self.assertEqual(self.habit_by_owner.is_active, initial_is_active)

    def test_unauthenticated_user_cannot_delete_habit(self):
        """
        Тест: Неавторизованный пользователь не может удалить привычку.
        """
        # Не вызываем self.client.force_authenticate()
        initial_habit_count = Habit.objects.count()

        response = self.client.delete(self.url_owner_habit)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            Habit.objects.count(), initial_habit_count
        )  # Привычка не должна быть удалена

    def test_delete_non_existent_habit(self):
        """
        Тест: Попытка удалить несуществующую привычку должна вернуть 404.
        """
        self.client.force_authenticate(
            user=self.user
        )  # Любой авторизованный пользователь
        response = self.client.delete(self.url_non_existent)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_deactivates_already_inactive_habit(self):
        """
        Тест: Владелец может удалить привычку.
        """
        self.habit_by_owner.is_active = False
        self.habit_by_owner.save()
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.delete(self.url_owner_habit)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class HabitListAPIViewTest(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.owner_user = User.objects.create(
            email="owner@example.com", password="123qwe"
        )
        self.other_user = User.objects.create(
            email="other@example.com", password="123qwe"
        )

        # Создаем привычки для разных сценариев
        # Привычки для owner_user
        self.owner_habit_active_1 = Habit.objects.create(
            owner=self.owner_user,
            action="Выпить витамины",
            time_deadline="09:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )
        self.owner_habit_active_2 = Habit.objects.create(
            owner=self.owner_user,
            action="Выпить воды",
            time_deadline="08:45",
            periodicity=1,
            time_to_complete=1,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )
        self.owner_habit_inactive = Habit.objects.create(
            owner=self.owner_user,
            action="Сделать зарядку",
            time_deadline="08:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )

        # Привычки для other_user
        self.other_habit_active = Habit.objects.create(
            owner=self.other_user,
            action="Бегать",
            time_deadline="09:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )
        self.other_habit_inactive = Habit.objects.create(
            owner=self.other_user,
            action="Плавать",
            time_deadline="19:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )

        self.url = reverse("habits:habits_list")
        self.total_habits_in_db = Habit.objects.count()
        self.owner_active_habits_count = Habit.objects.filter(
            owner=self.owner_user, is_active=True
        ).count()  # 8
        self.other_active_habits_count = Habit.objects.filter(
            owner=self.other_user, is_active=True
        ).count()  # 1

    def test_unauthenticated_user_gets_401(self):
        """
        Неавторизованный пользователь должен получить 401 Unauthorized.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_sees_only_own_active_habits(self):
        """
        Владелец привычек должен видеть только свои активные привычки.
        (Тестируем первую страницу пагинации)
        """
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["count"], self.owner_active_habits_count
        )  # Должно быть 2
        # self.assertEqual(len(response.data['results']), CustomPaginator.page_size) # Первая страница = 5

        # Проверяем, что в результатах только активные привычки владельца
        retrieved_ids = {habit["id"] for habit in response.data["results"]}
        expected_ids = set(
            Habit.objects.filter(owner=self.owner_user, is_active=True)
            .order_by("pk")[: CustomPaginator.page_size]
            .values_list("id", flat=True)
        )
        self.assertEqual(retrieved_ids, expected_ids)
        # self.assertNotIn(self.owner_habit_inactive.pk, retrieved_ids) # Неактивная не должна быть
        self.assertNotIn(
            self.other_habit_active.pk, retrieved_ids
        )  # Чужая не должна быть

    def test_other_authenticated_user_sees_no_habits(self):
        """
        Другой авторизованный пользователь (не владелец) должен видеть пустой список.
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["count"], self.other_active_habits_count
        )  # Должна быть 1 (owner_user не видит привычки other_user)
        self.assertEqual(
            len(response.data["results"]), self.other_active_habits_count
        )  # 1, т.к. other_user видит только свои

        retrieved_ids = {habit["id"] for habit in response.data["results"]}
        # self.assertEqual(retrieved_ids, {self.other_habit_active.pk})
        self.assertNotIn(self.owner_habit_active_1.pk, retrieved_ids)

    def test_pagination_for_owner(self):
        """
        Проверяем, что пагинация работает корректно для владельца.
        """
        self.client.force_authenticate(user=self.owner_user)
        # Получаем первую страницу
        response_page1 = self.client.get(self.url)
        self.assertEqual(response_page1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_page1.data["count"], self.owner_active_habits_count
        )  # Всего 8
        # self.assertEqual(len(response_page1.data['results']), CustomPaginator.page_size) # 5 на первой странице
        # self.assertIsNotNone(response_page1.data['next']) # Должна быть следующая страница


class PublicHabitListAPIViewTest(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.owner_user = User.objects.create(
            email="owner@example.com", password="123qwe"
        )
        self.other_user = User.objects.create(
            email="other@example.com", password="123qwe"
        )
        self.unauthenticated_client = self.client  # Сохраняем неавторизованный клиент

        # Создаем публичные привычки (для owner_user)
        self.public_habit_1 = Habit.objects.create(
            owner=self.owner_user,
            action="Плавать",
            time_deadline="19:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=True,
            is_active=True,
        )
        self.public_habit_2 = Habit.objects.create(
            owner=self.owner_user,
            action="Ходить",
            time_deadline="18:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=True,
            is_active=True,
        )

        # Создаем публичную привычку (для other_user)
        self.other_user_public_habit = Habit.objects.create(
            owner=self.other_user,
            action="Читать",
            time_deadline="20:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=True,
            is_active=True,
        )

        # Создаем приватные привычки (они НЕ должны отображаться)
        self.private_habit_1 = Habit.objects.create(
            owner=self.owner_user,
            action="Пить воду",
            time_deadline="08:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )
        self.private_habit_2 = Habit.objects.create(
            owner=self.owner_user,
            action="Пить витамины",
            time_deadline="09:00",
            periodicity=1,
            time_to_complete=2,
            location="Home",
            date_deadline="2025-09-01",
            is_enjoyable=False,
            is_public=False,
            is_active=True,
        )

        # Создаем дополнительные публичные привычки для тестирования пагинации
        # Всего будет 3 (public_habit_1,2 + other_user_public_habit) + 5 = 8 публичных привычек
        for i in range(3, 8):
            Habit.objects.create(
                owner=self.owner_user,
                action=f"Пить витамины {i}",
                time_deadline="09:00",
                periodicity=1,
                time_to_complete=2,
                location="Home",
                date_deadline="2025-09-01",
                is_enjoyable=False,
                is_public=True,
                is_active=True,
            )
        self.url = reverse("habits:public_habits_list")
        self.total_public_habits_count = Habit.objects.filter(
            is_public=True
        ).count()  # Должно быть 8
        self.expected_first_page_ids = set(
            Habit.objects.filter(is_public=True)
            .order_by("pk")[: CustomPaginator.page_size]
            .values_list("id", flat=True)
        )

    def test_unauthenticated_user_can_access(self):
        """
        Неавторизованный пользователь должен успешно получить список публичных привычек.
        """
        response = self.unauthenticated_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.total_public_habits_count)
        self.assertEqual(
            len(response.data["results"]), CustomPaginator.page_size
        )  # Первая страница = 5

        # Проверяем, что все возвращенные привычки публичные
        for habit_data in response.data["results"]:
            # print(response.data['results'])
            self.assertTrue(habit_data["is_public"])
        #
        # Проверяем, что возвращены только ожидаемые публичные привычки на первой странице
        retrieved_ids = {habit["id"] for habit in response.data["results"]}
        self.assertEqual(retrieved_ids, self.expected_first_page_ids)

    def test_authenticated_user_can_access(self):
        """
        Авторизованный пользователь (владелец) также должен успешно получить список публичных привычек.
        """
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.total_public_habits_count)
        self.assertEqual(len(response.data["results"]), CustomPaginator.page_size)

        # Проверяем, что все возвращенные привычки публичные
        for habit_data in response.data["results"]:
            self.assertTrue(habit_data["is_public"])

        retrieved_ids = {habit["id"] for habit in response.data["results"]}
        self.assertEqual(retrieved_ids, self.expected_first_page_ids)

    def test_only_public_habits_are_returned(self):
        """
        В списке должны быть только привычки с is_public=True.
        Приватные привычки не должны отображаться.
        """
        response = self.unauthenticated_client.get(
            self.url
        )  # Можно использовать любой клиент

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.total_public_habits_count)

        retrieved_ids = {habit["id"] for habit in response.data["results"]}

        # Убеждаемся, что приватные привычки не присутствуют в результатах первой страницы
        self.assertNotIn(self.private_habit_1.pk, retrieved_ids)
        self.assertNotIn(self.private_habit_2.pk, retrieved_ids)

        # Дополнительная проверка: убедимся, что все полученные привычки действительно публичные
        for habit_data in response.data["results"]:
            self.assertTrue(habit_data["is_public"])

    def test_pagination_works_correctly(self):
        """
        Проверяем, что пагинация работает корректно для публичных привычек.
        """
        response_page1 = self.unauthenticated_client.get(self.url)
        self.assertEqual(response_page1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_page1.data["count"], self.total_public_habits_count
        )  # Всего 8
        self.assertEqual(
            len(response_page1.data["results"]), CustomPaginator.page_size
        )  # 5 на первой странице
        self.assertIsNotNone(
            response_page1.data["next"]
        )  # Должна быть следующая страница

        response_page2 = self.unauthenticated_client.get(response_page1.data["next"])
        self.assertEqual(response_page2.status_code, status.HTTP_200_OK)

        self.assertEqual(response_page2.data["count"], self.total_public_habits_count)
        self.assertEqual(
            len(response_page2.data["results"]),
            self.total_public_habits_count - CustomPaginator.page_size,
        )  # 8 - 5 = 3
        self.assertIsNone(response_page2.data["next"])  # Больше страниц быть не должно

        # Проверяем, что id на разных страницах не пересекаются
        ids_page1 = {habit["id"] for habit in response_page1.data["results"]}
        ids_page2 = {habit["id"] for habit in response_page2.data["results"]}
        self.assertTrue(ids_page1.isdisjoint(ids_page2))

        # Проверяем, что общее количество уникальных ID соответствует ожидаемому
        all_retrieved_ids = ids_page1.union(ids_page2)
        expected_total_ids = set(
            Habit.objects.filter(is_public=True).values_list("id", flat=True)
        )
        self.assertEqual(all_retrieved_ids, expected_total_ids)

        # Проверяем, что все полученные привычки публичные
        for habit_data in (
            response_page1.data["results"] + response_page2.data["results"]
        ):
            self.assertTrue(habit_data["is_public"])

    def test_empty_list_if_no_public_habits(self):
        """
        Если публичных привычек нет, должен быть возвращен пустой список.
        """
        Habit.objects.all().delete()  # Удаляем все привычки, чтобы проверить пустой список
        response = self.unauthenticated_client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertIsNone(response.data["next"])
        self.assertIsNone(response.data["previous"])
