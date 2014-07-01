from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('earmarkwatch.users.views',

    url(r'^update-profile/$', 'update_profile', name='update_profile'),

    url(r'^(?P<username>\w+)/$', 'user_view', name='user_view'),
    url(r'^(?P<username>\w+)/(?P<tab>(comments|messages|earmarks|manage))/$', 'user_view', name='user_view_tab'),
    url(r'^(?P<username>\w+)/(?P<tab>(comments|messages|earmarks))/(?P<page_num>\d+)/$', 'user_view', name='user_view_tab_page'),
)
