from datetime import datetime
from django.test import TestCase

from escolar.core.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.obj = User(
                        email='email@usuario.com',
                        nome='usuario nome',
                        is_active=True,
                        nascimento='2005-09-20',
                        profissao='Aluno',
                        sexo=2,
                        )
        self.obj.save()

    def test_create(self):
        self.assertTrue(User.objects.exists())

    def test_created_at(self):
        """User must have an auto created_at attr"""
        self.assertIsInstance(self.obj.created_at, datetime)

    def test_unicode(self):
        self.assertEqual(str(self.obj), 'email@usuario.com')
