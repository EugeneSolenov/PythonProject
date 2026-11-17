from django.db import models


class User(models.Model):
    """Модель пользователя (члена семьи)."""

    name = models.CharField(
        max_length=150,
        verbose_name="Имя",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.name
