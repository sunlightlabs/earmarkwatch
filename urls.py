from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    (r'^', include('earmarkwatch.research.urls')),
    (r'^', include('sharedauth.urls')),
    (r'^user/', include('earmarkwatch.users.urls')),
    (r'^admin/(.*)', admin.site.root),
)
