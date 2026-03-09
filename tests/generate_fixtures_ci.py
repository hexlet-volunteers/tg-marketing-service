#!/usr/bin/env python
"""Скрипт для генерации фикстур в CI"""

import os
import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    import django
    django.setup()
    
    from tests.generate_fixtures import ModelAndFormFixtureGenerator
    
    print('🔄 Generating fixtures...')
    generator = ModelAndFormFixtureGenerator()
    generator.generate_all()
    print('✅ Fixtures generated!')

if __name__ == "__main__":
    main()