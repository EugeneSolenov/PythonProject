from django.db import models


class Category(models.Model):
    """Модель категории событий семейного календаря."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Описание",
    )
    icon = models.CharField(
        max_length=20,
        default="📅",
        verbose_name="Иконка",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f"{self.icon} {self.name}"
