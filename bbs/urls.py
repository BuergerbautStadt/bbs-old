from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

from views import VeroeffentlichungenFeed

#from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
#from django.contrib import admin
from django.conf import settings
import os.path

from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailsearch.urls import frontend as wagtailsearch_frontend_urls

admin.autodiscover()

# Signal handlers
from wagtail.wagtailsearch import register_signal_handlers as wagtailsearch_register_signal_handlers
wagtailsearch_register_signal_handlers()

urlpatterns = patterns('',
    #url(r'^$', 'bbs.views.home'),
    # orte
    url(r'^orte/$', 'bbs.views.orte'),
    url(r'^orte/(?P<pk>\d+)/$', 'bbs.views.ort'),
    #url(r'^orte/neu/$', 'bbs.views.ort'),
    # veroeffentlichungen
    url(r'^veroeffentlichungen/neu/$', 'bbs.views.create_veroeffentlichung'),
    url(r'^veroeffentlichungen/feed/$', VeroeffentlichungenFeed(), name="feedsurl"),
    # begriffe
    url(r'^begriffe/$', 'bbs.views.begriffe'),
    # modules
    url(r'^news/', include('news.urls')),
    url(r'^projekte/', include('projects.urls')),
    # url(r'^visualization/', include('visualization.urls')),
    # admin foo
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # user login
    url(r'^login/', 'bbs.views.login_user'),
    url(r'^logout/', 'bbs.views.logout_user'),
    # robots.txt and sitemap.xml
    (r'^robots\.txt$', TemplateView.as_view(template_name='bbs/robots.txt', content_type='text/plain')),
    (r'^sitemap\.xml$', TemplateView.as_view(template_name='bbs/sitemap.xml', content_type='text/plain')),

    #url(r'^django-admin/', include(admin.site.urls)),

    url(r'^cms-admin/', include(wagtailadmin_urls)),
    url(r'^search/', include(wagtailsearch_frontend_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's serving mechanism
    url(r'', include(wagtail_urls)),
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns() # tell gunicorn where static files are in dev mode
    urlpatterns += static(settings.MEDIA_URL + 'images/', document_root=os.path.join(settings.MEDIA_ROOT, 'images'))
    urlpatterns += patterns('',
        (r'^favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL + 'myapp/images/favicon.ico'))
    )
