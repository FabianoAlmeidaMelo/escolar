from datetime import datetime
from django.test import TestCase

from escolar.core.models import User

'''
python manage.py test escolar.core.testes.test_models_user
'''

class UserModelTest(TestCase):
    def setUp(self):
        self.obj = User(email='email@usuario.com',
                        username='email@usuario.com',
                        nome='usuario nome',
                        is_active=True,)
        self.obj.save()

    def test_create(self):
        self.assertTrue(User.objects.exists())

    def test_created_at(self):
        """User must have an auto created_at attr"""
        self.assertIsInstance(self.obj.date_joined, datetime)

    def test_str(self):
        self.assertEqual(str(self.obj), 'usuario nome')
