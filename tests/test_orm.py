import os
from datetime import date
import django
from django.core.paginator import Paginator
from django.db.models import Count, Max, Min, ProtectedError, Q
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "family_calendar.settings")
django.setup()

from categories.models import Category  # noqa: E402
from events.models import Event          # noqa: E402
from users.models import User            # noqa: E402


class DjangoORMTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat_study, _ = Category.objects.get_or_create(
            id=10,
            defaults={
                "name": "Тестовая учёба",
                "description": "Тестовое описание",
                "icon": "📖",
            },
        )
        cls.cat_holidays, _ = Category.objects.get_or_create(
            id=11,
            defaults={
                "name": "Тестовые праздники",
                "description": "Праздничные дни",
                "icon": "🎉",
            },
        )
        cls.cat_empty, _ = Category.objects.get_or_create(
            id=12,
            defaults={
                "name": "Пустая тестовая категория",
                "description": "Без событий",
                "icon": "⭐",
            },
        )

        cls.user_eugene, _ = User.objects.get_or_create(
            id=10,
            defaults={
                "name": "Тестовый Евгений",
                "email": "test_eugene@example.com",
            },
        )
        cls.user_anna, _ = User.objects.get_or_create(
            id=11,
            defaults={
                "name": "Тестовая Анна",
                "email": "test_anna@example.com",
            },
        )

        cls.ev1 = Event.objects.create(
            id=101,
            user=cls.user_eugene,
            category=cls.cat_study,
            name="Подготовка к экзамену",
            event_date=date(2026, 11, 20),
            is_completed=False,
        )
        cls.ev2 = Event.objects.create(
            id=102,
            user=cls.user_eugene,
            category=cls.cat_holidays,
            name="Семейный Новый Год",
            event_date=date(2026, 12, 31),
            is_completed=False,
        )
        cls.ev3 = Event.objects.create(
            id=103,
            user=cls.user_anna,
            category=cls.cat_study,
            name="Сдача курсового проекта",
            event_date=date(2026, 11, 15),
            is_completed=True,
        )

    def test_models_string_representation(self):
        """Проверка строковых представлений моделей (__str__)."""
        self.assertIn("Тестовая учёба", str(self.cat_study))
        self.assertIn("Тестовый Евгений", str(self.user_eugene))
        self.assertIn("Подготовка к экзамену", str(self.ev1))

    def test_model_methods(self):
        """Проверка методов моделей (complete, days_until, is_upcoming)."""
        ev = Event.objects.get(pk=101)
        self.assertFalse(ev.is_completed)
        ev.complete()
        ev.refresh_from_db()
        self.assertTrue(ev.is_completed)

        days = ev.days_until(today=date(2026, 11, 10))
        self.assertEqual(days, 10)

    def test_foreign_key_and_reverse_relations(self):
        """Проверка прямых и обратных связей между моделями."""
        ev = Event.objects.select_related("category", "user").get(pk=101)
        self.assertEqual(ev.category.name, "Тестовая учёба")
        self.assertEqual(ev.user.name, "Тестовый Евгений")

        # Обратная связь related_name="events"
        category_events = self.cat_study.events.all()
        self.assertEqual(category_events.count(), 2)

        user_events = self.user_eugene.events.all()
        self.assertEqual(user_events.count(), 2)

    def test_on_delete_protect_constraint(self):
        """Проверка целостности: нельзя удалить категорию с событиями."""
        with self.assertRaises(ProtectedError):
            self.cat_study.delete()

    def test_filtering_and_exclude(self):
        """Проверка фильтрации: filter по полю, связи и exclude."""
        # Фильтр по одному полю
        completed = Event.objects.filter(is_completed=True)
        self.assertTrue(completed.filter(pk=103).exists())

        # Исключение записей через exclude()
        active = Event.objects.exclude(is_completed=True)
        self.assertFalse(active.filter(pk=103).exists())

        # Фильтр по полю связанной модели
        study_events = Event.objects.filter(category__name="Тестовая учёба")
        self.assertEqual(study_events.count(), 2)

        # Фильтр по нескольким условиям
        filtered = Event.objects.filter(
            category=self.cat_study,
            is_completed=False,
        )
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().pk, 101)

    def test_search_with_q_objects(self):
        """Проверка поиска по нескольким полям с использованием Q-объектов."""
        # Поиск по названию
        res1 = Event.objects.filter(id__in=[101, 102, 103]).filter(
            name__icontains="экзамен"
        )
        self.assertEqual(res1.count(), 1)

        # Поиск по названию или имени члена семьи
        res2 = Event.objects.filter(id__in=[101, 102, 103]).filter(
            Q(name__icontains="Новый") | Q(user__name__icontains="Анна")
        )
        self.assertEqual(res2.count(), 2)

    def test_sorting(self):
        """Проверка сортировки по дате, названию и связанной модели."""
        by_date = list(
            Event.objects.filter(id__in=[101, 102, 103])
            .order_by("event_date")
            .values_list("id", flat=True)
        )
        self.assertEqual(by_date, [103, 101, 102])

        # "Тестовая учёба" идёт раньше "Тестовые праздники" (буква 'а' < 'ы')
        by_cat = list(
            Event.objects.filter(id__in=[101, 102])
            .order_by("category__name")
            .values_list("id", flat=True)
        )
        self.assertEqual(by_cat, [101, 102])

    def test_aggregation_and_annotation(self):
        """Проверка агрегации (aggregate) и аннотации (annotate Count)."""
        agg = Event.objects.filter(id__in=[101, 102, 103]).aggregate(
            total=Count("id"),
            earliest=Min("event_date"),
            latest=Max("event_date"),
        )
        self.assertEqual(agg["total"], 3)
        self.assertEqual(agg["earliest"], date(2026, 11, 15))
        self.assertEqual(agg["latest"], date(2026, 12, 31))

        # Аннотация со счётчиком событий (включая пустые категории)
        cats = Category.objects.filter(id__in=[10, 11, 12]).annotate(
            events_count=Count("events")
        ).order_by("id")

        stats = {c.id: c.events_count for c in cats}
        self.assertEqual(stats[10], 2)
        self.assertEqual(stats[11], 1)
        self.assertEqual(stats[12], 0)  # Пустая категория выводит 0!

    def test_paginator(self):
        """Проверка работы пагинатора Paginator."""
        qs = Event.objects.order_by("pk")
        paginator = Paginator(qs, 2)
        self.assertGreaterEqual(paginator.num_pages, 2)

        page1 = paginator.get_page(1)
        self.assertEqual(len(page1), 2)
        self.assertTrue(page1.has_next())

        # Некорректный номер страницы возвращает 1-ю страницу
        page_invalid = paginator.get_page("invalid")
        self.assertEqual(page_invalid.number, 1)
