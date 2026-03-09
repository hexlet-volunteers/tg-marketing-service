#!/usr/bin/env python
"""Скрипт для генерации фикстур в CI"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def main():
    # Устанавливаем настройки Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Инициализируем Django
    import django
    django.setup()
    
    # Импортируем генератор
    from tests.generate_fixtures import ModelAndFormFixtureGenerator
    
    print('🔄 Generating fixtures...')
    generator = ModelAndFormFixtureGenerator()
    generator.generate_all()
    print('✅ Fixtures generated!')

if __name__ == "__main__":
    main()