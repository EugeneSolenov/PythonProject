from datetime import date
from django.db import models

from categories.models import Category
from users.models import User


class Event(models.Model):
    """Модель события семейного календаря."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Пользователь",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Категория",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название события",
    )
    event_date = models.DateField(
        verbose_name="Дата события",
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name="Событие завершено",
    )

    class Meta:
        ordering = ["event_date", "pk"]
        verbose_name = "Событие"
        verbose_name_plural = "События"

    def __str__(self):
        status = "выполнено" if self.is_completed else "запланировано"
        return f"{self.name} — {self.event_date} ({self.category.name}, {status})"

    def complete(self):
        """Помечает событие как выполненное."""
        self.is_completed = True
        self.save(update_fields=["is_completed"])

    def mark_completed(self):
        """Синоним complete для обратной совместимости."""
        self.complete()

    def days_until(self, today=None):
        """Количество дней до события."""
        current_date = today or date.today()
        return (self.event_date - current_date).days

    def is_upcoming(self, today=None):
        """Проверяет, является ли событие предстоящим."""
        return self.days_until(today) >= 0 and not self.is_completed
