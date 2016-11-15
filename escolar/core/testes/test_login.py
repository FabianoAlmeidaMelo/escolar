from django.test import TestCase
from django.shortcuts import resolve_url
from escolar.core.forms import AuthenticationForm

class LoginTest(TestCase):

    def setUp(self):
        self.response = self.client.get(resolve_url('login'))

    def test_get(self):
        """GET /login/ must return status code 200"""
        # response = self.client.get('/')
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use login.html"""
        # response = self.client.get('/')
        self.assertTemplateUsed(self.response, 'login.html')

    def test_html(self):
        """Must conatain input tags"""
        tags = (('<form', 1),
                ('<input', 4),
                ('type="text"', 2),
                ('type="submit"', 1),
            )
        for txt, count in tags:
            with self.subTest():
                self.assertContains(self.response, txt, count)

    def test_crsf(self):
        """Html must coantain csrf"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')


    def test_has_form(self):
        """Context must have LoginTest form"""
        form = self.response.context['form']
        self.assertIsInstance(form, AuthenticationForm)

    def test_form_has_fields(self):
        """Form must have 3 fields"""
        form = self.response.context['form']
        self.assertSequenceEqual(['username', 'password', 'keep_me_logged_in'], list(form.fields))



    # def test_talks_link(self):
    #     """Must show keynote talks link"""
    #     expected = 'href="{}"'.format(resolve_url('talk_list'))
    #     self.assertContains(self.response, expected)
