from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Category:
    id: int
    name: str
    description: str = ""
    icon: str = "📅"

    def __str__(self) -> str:
        return f"{self.icon} {self.name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Category":
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            description=str(data.get("description", "")),
            icon=str(data.get("icon", "📅")),
        )


def find_category_by_id(
    categories: list[Category],
    category_id: int,
) -> Optional[Category]:
    """Найти категорию по идентификатору."""
    for category in categories:
        if category.id == category_id:
            return category
    return None


__all__ = ["Category", "find_category_by_id"]
