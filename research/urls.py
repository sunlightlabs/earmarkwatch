from django.conf.urls.defaults import *
from django.conf import settings

from earmarkwatch.research.models import Answer, Comment
from earmarkwatch.research.feeds import EarmarkFeed, UserFeed

urlpatterns = patterns('earmarkwatch.research.views',

    # index
    url(r'^$', 'index', name='index'),
    url(r'^faq/$', 'faq', name='faq'),
    url(r'^mapped/$', 'mapped', name='mapped'),

    url(r'^recent_comments/$', 'recent_comments', name='recent_comments'),
    url(r'^most_comments/$', 'most_comments', name='most_comments'),
    url(r'^recent_research/$', 'recent_research', name='recent_research'),

    # view an earmark
    url(r'^earmark/(?P<eid>\d+)/$', 'earmark_view', name='earmark_view'),

    # all of a sponsors earmarks within a bill
    url(r'^(?P<year>\d+)-(?P<chamber>\w+)-(?P<bill>\w+)/sponsor/(?P<id>\d+)/$',
        'sponsor_view', name='sponsor_view'),

    # most active earmarks in bill
    url(r'^(?P<year>\d+)-(?P<chamber>\w+)-(?P<bill>\w+)/$',
        'active', name='bill_view'),

    # random earmark from bill
    url(r'^(?P<year>\d+)-(?P<chamber>\w+)-(?P<bill>\w+)/random-earmark/$',
        'random_earmark', name='random_earmark'),

    # search within bill
    url(r'^(?P<year>\d+)-(?P<chamber>\w+)-(?P<bill>\w+)/search/$',
        'search', name='search'),

    ## POST-only ##

    # comments
    url(r'^post-earmark-comment/$', 'post_comment', {'type':Comment.EARMARK},
        name='post_earmark_comment'),
    url(r'^post-user-comment/$', 'post_comment', {'type':Comment.USER},
        name='post_user_comment'),

    # flagging
    url(r'^flag-answer/(?P<id>\d+)/$', 'flag', {'type':Answer}),
    url(r'^flag-comment/(?P<id>\d+)/$', 'flag', {'type':Comment}),
    url(r'^flag-answers-for/(?P<earmark_id>\d+)/$', 'flag_answers_for'),

)

# RSS feeds
feeds = {
    'earmark': EarmarkFeed,
    'user': UserFeed
}
urlpatterns += patterns('',
    (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '../earmarkwatch/static'}),
    )
