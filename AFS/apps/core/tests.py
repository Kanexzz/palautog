from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view_get_anonymous_user(self):
        """Test index view with anonymous user redirects to login"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_index_view_context(self):
        """Test index view has correct context data"""
        response = self.client.get(reverse('index'))
        context = response.context
        self.assertEqual(context['logo_text'], 'CHMSU')
        self.assertEqual(context['site_name'], 'Faculty Scheduling System')


class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )

    def test_dashboard_view_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_dashboard_view_authenticated_user(self):
        """Test dashboard view with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')
