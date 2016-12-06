from django.test import TestCase
from django.shortcuts import resolve_url
from escolar.escolas.models import Escola


class EscolaTest(TestCase):

    def setUp(self):
        self.response = self.client.get(resolve_url('escolas_list'))

    def test_get(self):
        """GET / must return status code 200"""
        # response = self.client.get('/')
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use escolas_list.html"""
        self.assertTemplateUsed(self.response, 'escolas_list.html')


    # def test_speackers_link(self):
    #     """Must show keynote speakers  link"""
    #     expected = 'href="{}#speakers"'.format(resolve_url('home'))
    #     self.assertContains(self.response, expected)

    # def test_talks_link(self):
    #     """Must show keynote talks link"""
    #     expected = 'href="{}"'.format(resolve_url('talk_list'))
    #     self.assertContains(self.response, expected)
