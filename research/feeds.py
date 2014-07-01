from django.contrib.syndication.feeds import Feed, FeedDoesNotExist

from earmarkwatch.research.models import Earmark, User

class EarmarkFeed(Feed):

    def title(self, earmark):
        return str(earmark)

    def link(self, earmark):
        if not earmark:
            raise FeedDoesNotExist
        return '/rss/earmark/%s' % earmark.id

    def description(self, earmark):
        return 'EarmarkWatch.org feed for %s' % earmark

    def items(self, earmark):
        items = list(earmark.answer_set.order_by('submit_date'))
        comments = list(earmark.comment_set.order_by('submit_date'))
        next = 0
        for idx, ans in enumerate(comments):
            while next < len(comments) and comments[next].submit_date < ans.submit_date:
                items.insert(idx, comments[next])
                next += 1
        items += comments[next:]
        return items

    def get_object(self, bits):
        if len(bits) != 1:
            raise FeedDoesNotExist
        return Earmark.objects.get(pk=bits[0])

    def item_author_name(self, item):
        return item.user

    def item_author_link(self, ans):
        return '/user/%s/' % (ans.user)

    def item_pubdate(self, item):
        return item.submit_date


class UserFeed(Feed):

    def title(self, user):
        return 'EarmarkWatch.org feed for %s' % user

    def link(self, user):
        if not user:
            raise FeedDoesNotExist
        return '/rss/user/%s' % user

    def description(self, user):
        return 'EarmarkWatch.org feed for %s' % user

    def items(self, user):
        items = list(user.answer_set.order_by('submit_date'))
        comments = list(user.comment_set.order_by('submit_date'))
        next = 0
        for idx, ans in enumerate(comments):
            while next < len(comments) and comments[next].submit_date < ans.submit_date:
                items.insert(idx, comments[next])
                next += 1
        items += comments[next:]
        return items

    def get_object(self, bits):
        if len(bits) != 1:
            raise FeedDoesNotExist
        return User.objects.get(username=bits[0])

    def item_author_name(self, item):
        return item.user

    def item_author_link(self, ans):
        return '/user/%s/' % (ans.user)

    def item_pubdate(self, item):
        return item.submit_date
