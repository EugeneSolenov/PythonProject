import os
import django
from django.test import Client, SimpleTestCase
from django.test.utils import setup_test_environment
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "family_calendar.settings")
django.setup()
setup_test_environment()


class WebInterfaceTests(SimpleTestCase):
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
        self.assertContains(response, "Всего событий:")

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
