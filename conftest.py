# conftest.py
import os
import sys

# Добавляем корень проекта в sys.path, чтобы Python видел все подпапки
sys.path.append(os.path.dirname(__file__))

# Устанавливаем DJANGO_SETTINGS_MODULE на внутреннюю папку с настройками
# Bнимание: используем только папку внутри проекта без дефисов!
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
