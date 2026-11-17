import os
from datetime import date
import django
from django.test import Client, TestCase
from django.test.utils import setup_test_environment
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "family_calendar.settings")
django.setup()
setup_test_environment()

from categories.models import Category  # noqa: E402
from events.models import Event          # noqa: E402
from users.models import User            # noqa: E402


class WebInterfaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat1, _ = Category.objects.get_or_create(
            id=1,
            defaults={
                "name": "Праздники и памятные даты",
                "description": "Семейные праздники",
                "icon": "🎉",
            },
        )
        cat2, _ = Category.objects.get_or_create(
            id=2,
            defaults={
                "name": "Учёба и работа",
                "description": "Сдача работ",
                "icon": "📚",
            },
        )
        user1, _ = User.objects.get_or_create(
            id=1,
            defaults={
                "name": "Евгений Соленов",
                "email": "solenov@example.com",
            },
        )
        user2, _ = User.objects.get_or_create(
            id=2,
            defaults={
                "name": "Анна Иванова",
                "email": "anna@example.com",
            },
        )
        Event.objects.get_or_create(
            id=1,
            defaults={
                "user": user1,
                "category": cat2,
                "name": "Защита ПР5 и ПР6 по Django",
                "event_date": date(2026, 10, 20),
                "is_completed": False,
            },
        )
        Event.objects.get_or_create(
            id=2,
            defaults={
                "user": user2,
                "category": cat1,
                "name": "Семейный праздник и ужин",
                "event_date": date(2026, 10, 25),
                "is_completed": False,
            },
        )

    def setUp(self):
        self.client = Client()

    def test_homepage_view(self):
        response = self.client.get(reverse("homepage:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "homepage/index.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Семейный календарь")
        self.assertContains(response, "Всего событий")

    def test_events_list_view(self):
        response = self.client.get(reverse("events:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_list.html")
        self.assertTemplateUsed(response, "events/includes/event_card.html")
        self.assertContains(response, "событий:")

    def test_event_detail_existing(self):
        url = reverse("events:detail", kwargs={"event_id": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_detail.html")
        self.assertContains(response, "Категория:")
        self.assertContains(response, "к списку событий")

    def test_event_detail_not_found(self):
        url = reverse("events:detail", kwargs={"event_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "events/event_detail.html")
        self.assertContains(response, "Событие не найдено", status_code=404)

    def test_categories_list_view(self):
        response = self.client.get(reverse("categories:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/category_list.html")
        self.assertTemplateUsed(
            response,
            "categories/includes/category_card.html",
        )
        self.assertContains(response, "Всего категорий:")

    def test_category_detail_existing(self):
        url = reverse("categories:detail", kwargs={"category_id": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "categories/category_detail.html")
        self.assertContains(response, "к списку категорий")

    def test_category_detail_not_found(self):
        url = reverse("categories:detail", kwargs={"category_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "categories/category_detail.html")
        self.assertContains(response, "Категория не найдена", status_code=404)

    def test_events_search_view(self):
        # GET запрос без параметров даты
        response = self.client.get(reverse("events:search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/search.html")
        self.assertContains(response, "Поиск событий по дате")

        # GET запрос с параметром даты
        response_with_date = self.client.get(
            reverse("events:search"),
            {"date": "2026-10-20"},
        )
        self.assertEqual(response_with_date.status_code, 200)
        self.assertTemplateUsed(response_with_date, "events/search.html")
        self.assertContains(response_with_date, "2026-10-20")

    def test_events_statistics_view(self):
        response = self.client.get(reverse("events:statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/statistics.html")
        self.assertContains(response, "Статистика семейного календаря")
        self.assertContains(response, "Распределение событий по категориям")

    def test_404_handler_for_unknown_path(self):
        with self.settings(DEBUG=False):
            response = self.client.get("/some-unknown-path-for-test/")
            self.assertEqual(response.status_code, 404)
            self.assertTemplateUsed(response, "404.html")
            self.assertContains(
                response,
                "Страница не найдена",
                status_code=404,
            )
