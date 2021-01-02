from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import logout

from django.contrib.auth.views import (
            LoginView,
            password_reset,
            password_reset_complete,
            password_reset_confirm,
            password_reset_done,
        )
# from escolar.core.forms import AuthenticationForm

from escolar.core.views import home

# autocomplete_light.autodiscover()  # before admin.autodiscover
admin.autodiscover()

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^(?P<escola_pk>\d+)/$', home, name='home'),
    url(r'^', include('escolar.core.urls')),
    url(r'^', include('escolar.escolas.urls')),
    url(r'^', include('escolar.financeiro.urls')),
    url(r'^', include('escolar.comunicacao.urls')),
    url(r'^', include('escolar.sites.urls')),

    # Logins
    url(r'^logout/$', logout, {"next_page": None}, name="logout"),
    url(r'^logout/(?P<next_page>.*)/$', logout, name='auth_logout_next'),
    # path('login/', LoginView.as_view(template_name='login.html'),

    url(r'^login/$', LoginView.as_view(template_name='login.html'),
        name="login"),

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
    url(r'^municipios_app/', include('municipios.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
