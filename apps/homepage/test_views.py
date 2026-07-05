from django.test import TestCase
from django.urls import reverse

from apps.homepage.models import HomePageComponent


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.component = HomePageComponent.objects.create(
            title="My Component Title",
            content="Some content here",
            order=1,
            is_active=True
        )

    def test_index_view_with_inertia_props(self):
        response = self.client.get(
            reverse('main_index'),
            HTTP_ACCEPT='application/json',
            HTTP_X_INERTIA='true',
        )

        self.assertEqual(response.status_code, 200)

        # Django test client автоматически декодирует JSON
        data = response.json()

        # Inertia-обёртка
        self.assertIn('component', data)
        self.assertIn('props', data)
        self.assertIn('url', data)
        self.assertIn('version', data)

        # Проверяем props
        props = data['props']
        self.assertIn('components', props)

        components = props['components']
        self.assertGreater(len(components), 0)

        first_component = components[0]
        self.assertEqual(first_component['title'], self.component.title)
        self.assertEqual(first_component['content'], self.component.content)
        self.assertEqual(first_component['order'], self.component.order)

