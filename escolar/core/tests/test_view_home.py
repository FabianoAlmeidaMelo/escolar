from django.test import TestCase
from django.shortcuts import resolve_url

'''
python manage.py test escolar.core.testes.test_view_home
'''

class HomeTest(TestCase):
    # fixtures = ['keynotes.json']
    def setUp(self):
        self.response = self.client.get(resolve_url('home'))

    def test_get(self):
        """GET / must return status code 200"""
        # response = self.client.get('/')
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use index.html"""
        self.assertTemplateUsed(self.response, 'index.html')


    def test_login_link(self):
        """Must show login  link"""
        expected = 'href="{}"'.format(resolve_url('login'))
        self.assertContains(self.response, expected)

    def test_home_link(self):
        """Must show keynote talks link"""
        expected = 'href="{}"'.format(resolve_url('home'))
        self.assertContains(self.response, expected)
