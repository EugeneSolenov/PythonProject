from models.categories import Category, find_category_by_id


def test_category_creation() -> None:
    cat = Category(1, "Праздники", "Семейные праздники", icon="🎉")
    assert cat.id == 1
    assert cat.name == "Праздники"
    assert cat.description == "Семейные праздники"
    assert "Праздники" in str(cat)


def test_find_category_by_id() -> None:
    cats = [
        Category(1, "Праздники"),
        Category(2, "Учёба"),
    ]
    found = find_category_by_id(cats, 2)
    assert found is not None
    assert found.name == "Учёба"
    assert find_category_by_id(cats, 999) is None
