from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.test import TestCase
from escolar.core.models import User
from escolar.escolas.models import Escola

'''
python manage.py test escolar.escolas.testes.test_views_escola_list
'''

class EscolaTest(TestCase):

    def setUp(self):
        self.obj = User(email='email@usuario.com',
                        username='email@usuario.com',
                        nome='usuario nome',
                        password='bar',
                        is_active=True,)
        self.obj.save()
        self.response = self.client.get(resolve_url('escolas_list'))

    def test_get(self):
        """GET / must return status code 302, não está logado, redireciona para o login"""
        # response = self.client.get('/')
        self.assertEqual(302, self.response.status_code)


    def test_that_user_gets_logged_in(self):
        response = self.client.post(reverse('login'), 
                                    { 'username':'email@usuario.com', 
                                      'password1':'bar', 
                                      'password2':'bar' } )

        user = User.objects.get(username='email@usuario.com')
        assert user.is_authenticated()


    # def test_profile(self):

    #     self.client.user = self.obj

    #     print(self.obj.id)

    #     request = self.client.get("/account/profile/{}/".format(self.obj.id), follow=True)
    #     self.assertEqual(request.status_code, 200)


    # def test_get_autenticado(self):
    #     """GET / must return status code 200, não está logado, redireciona para o login"""
    #     # response = self.client.get('/')
    #     response = self.client.post(reverse('login'), 
    #                                 { 'username':'email@usuario.com', 
    #                                   'password1':'bar', 
    #                                   'password2':'bar' } )

    #     user = User.objects.get(username='email@usuario.com')
    #     self.assertEqual(302, self.response.status_code)

    # def test_template(self):
    #     """Must use escolas_list.html"""
    #     self.assertTemplateUsed(self.response, 'escolas_list.html')

    # def test_speackers_link(self):
    #     """Must show keynote speakers  link"""
    #     expected = 'href="{}#speakers"'.format(resolve_url('home'))
    #     self.assertContains(self.response, expected)

    # def test_talks_link(self):
    #     """Must show keynote talks link"""
    #     expected = 'href="{}"'.format(resolve_url('talk_list'))
    #     self.assertContains(self.response, expected)
