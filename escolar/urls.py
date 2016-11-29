
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import (
            logout,
            login,
            password_reset,
            password_reset_complete,
            password_reset_confirm,
            password_reset_done,
        )
from escolar.core.forms import AuthenticationForm

from escolar.core.views import home

urlpatterns = [
    url(r'^$', home, name='home'),
    # Logins
    url(r'^logout/$', logout, {"next_page": "/"}, name="logout"),
    url(r'^login/$', login, {"template_name": 'login.html', "authentication_form": AuthenticationForm,}, name="login"),

    # password Reset
    url(
        r'^user/password/reset/$',
        password_reset,
        {'post_reset_redirect': '/user/password/reset/done/'},
        name="password_reset"
    ),
    url(r'^user/password/reset/done/$', password_reset_done),
    url(
        r'^user/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        password_reset_confirm,{'post_reset_redirect': '/user/password/done/'}
    ),
    url(r'^user/password/done/$', password_reset_complete),
    url(r'^admin/', admin.site.urls),
]
