from apps.parser.services.metrics import (
    average_reach,
    engagement_rate,
    growth_30d,
)


def test_engagement_rate():
    assert engagement_rate(10, 100) == 0.1
    assert engagement_rate(0, 100) == 0.0
    assert engagement_rate(10, 0) == 0.0
    assert engagement_rate(5, 20) == 0.25


def test_average_reach():
    assert average_reach(1000, 10) == 100.0
    assert average_reach(1000, 0) == 0.0
    assert average_reach(0, 10) == 0.0


def test_growth_30d():
    # Обычный рост
    assert growth_30d(150, 100) == (50, 50.0)
    # Падение
    assert growth_30d(80, 100) == (-20, -20.0)
    # Нулевой старт (защита от ZeroDivision)
    assert growth_30d(100, 0) == (100, 0.0)
    # Нет данных в прошлом (None)
    assert growth_30d(100, None) == (100, 0.0)
    # Стагнация
    assert growth_30d(100, 100) == (0, 0.0)
