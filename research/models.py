from django.db import models
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.localflavor.us.models import USStateField
from django.core.urlresolvers import reverse
#import gatekeeper

class Politician(models.Model):
    TITLES = (
        ('Sen', 'Senator'),
        ('Rep', 'Representative'))

    PARTIES = (
        ('D', 'Democrat'),
        ('I', 'Independent'),
        ('R', 'Republican'))

    title = models.CharField(max_length=3, choices=TITLES)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    party = models.CharField(max_length=1, choices=PARTIES)
    state = USStateField()
    district = models.IntegerField(null=True)
    website = models.URLField()
    photo = models.CharField(max_length=255)

    def calc_earmark_total(self, source_id):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('''SELECT SUM(appropriated) FROM research_earmark e,
                            research_earmark_sponsors es, research_politician p
                            WHERE e.id=es.earmark_id AND es.politician_id=p.id
                            AND p.id=%s AND e.source_id=%s''',
                            [self.id, source_id])
        amount = cursor.fetchone()[0]
        cursor.execute('''SELECT p.id FROM research_earmark e,
                            research_earmark_sponsors es, research_politician p
                            WHERE e.id=es.earmark_id AND es.politician_id=p.id
                            AND e.source_id=%s GROUP BY p.id
                            HAVING SUM(appropriated)>%s''', [source_id, amount])
        rank = cursor.rowcount
        return amount, rank

    def __str__(self):
        return '%s. %s (%s-%s)' % (self.title, self.lastname, self.party,
                                  self.state)

    class Meta:
        ordering = ['lastname','firstname','state']

class Source(models.Model):
    CHAMBERS = (
        ('house', 'House'),
        ('senate', 'Senate'))

    APPROPRIATION_TYPES = (
        ('laborhhs', 'Labor, Health and Human Services, and Education'),
        ('defense', 'Defense'),
        ('transportation', 'Transportation, HUD and Related Agencies'))

    YEARS = (
        (2008, 2008),
        (2007, 2007),
        (2009, 2009),
        (2010, 2010))

    id = models.IntegerField(primary_key=True)
    chamber = models.CharField(max_length=6, choices=CHAMBERS)
    type = models.CharField(max_length=30, choices=APPROPRIATION_TYPES)
    year = models.PositiveSmallIntegerField(choices=YEARS)

    def __str__(self):
        return '%s %s Appropriations, FY%s' % (self.get_chamber_display(),
                               self.get_type_display(),
                               self.year)

class EarmarkManager(models.Manager):
    def get_query_set(self):
        return super(EarmarkManager, self).get_query_set().extra(select={
            'is_big': 'appropriated >= 200000',
            'percent_answered': '''SELECT 100*COUNT(*)/(SELECT COUNT(*) FROM
                                    research_question) FROM research_answer
                                    WHERE earmark_id=research_earmark.id ''',
            'recently': '''SELECT MAX(submit_date) FROM research_answer WHERE earmark_id=research_earmark.id'''
                                     })

    def order_by_popularity(self):
        return self.extra(select={'num_comments': 'SELECT COUNT(*) FROM research_comment WHERE earmark_id=research_earmark.id',
                                  'latest_comment': 'SELECT MAX(submit_date) FROM research_comment WHERE earmark_id=research_earmark.id'},
                          order_by=('-num_comments', '-percent_answered', '-latest_comment'))

    def order_by_activity(self):
        return self.extra(select={'latest_comment': 'SELECT MAX(submit_date) FROM research_comment WHERE earmark_id=research_earmark.id',
                                  'mostviews': 'SELECT MAX(views) FROM research_earmarkinfo WHERE earmark_id=research_earmark.id limit 5',
                                  'num_comments': 'SELECT COUNT(*) FROM research_comment WHERE earmark_id=research_earmark.id',
                                  'lastmodified': 'SELECT MAX(submit_date) FROM research_answer WHERE earmark_id=research_earmark.id limit 5'},
                          order_by=('-mostviews', 'num_comments', '-lastmodified', '-latest_comment' ))

    def order_by_mostcomments(self):
        return self.extra(select={'num_comments': 'SELECT COUNT(*) FROM research_comment WHERE earmark_id=research_earmark.id'},
                          order_by=('-num_comments',))

    def order_by_mostviews(self):
        return self.extra(select={'mostviews': 'SELECT MAX(views) FROM research_earmarkinfo WHERE earmark_id=research_earmark.id'},
                          order_by=('-mostviews',))

    def order_by_lastmodified(self):
        return self.extra(select={'lastmodified': 'SELECT MAX(submit_date) FROM research_answer WHERE earmark_id=research_earmark.id'},
                          order_by=('-lastmodified',))

    def order_by_virgin(self):
        return self.extra(select={'virgin': 'SELECT MAX(views) FROM research_earmarkinfo WHERE earmark_id=research_earmark.id'}
                          ).order_by('?')

    def order_by_completed(self):
        return self.extra(select={'completed': 'SELECT MAX(views) FROM research_earmarkinfo WHERE earmark_id=research_earmark.id AND finished_on IS NOT NULL'},
                          order_by=('-completed', '-percent_answered'))

    def order_by_inprogress(self):
        return self.extra(select={'incompleted': '''SELECT MAX(views) finished_on FROM research_earmarkinfo WHERE earmark_id=research_earmark.id AND finished_on is NULL GROUP BY views DESC''',
                          'inprogress': 'SELECT MAX(submit_date) FROM research_answer WHERE earmark_id=research_earmark.id'},
                          order_by=('-incompleted',))

    def researched_by(self, eid):
        return self.extra(where=['''research_earmark.id IN
                                 (select distinct earmark_id from
                                 research_answer where user_id=%s)''' % eid],
                          )

class Earmark(models.Model):
    id = models.IntegerField(primary_key=True)
    appropriated = models.IntegerField()
    description = models.TextField()
    source = models.ForeignKey(Source)
    sponsors = models.ManyToManyField(Politician)

    objects = EarmarkManager()

    def amount_str(self):
        if self.appropriated == 0:
            return 'Classified Amount'
        else:
            return '$' + intcomma(self.appropriated)

    def get_absolute_url(self):
        return reverse('earmark_view', args=[self.id])

    def __str__(self):
        recips = self.location_set.all()
        recipstr = ''
        if len(recips) == 1 and recips[0].name:
            recipstr = ' to ' + recips[0].name
        elif len(recips) > 1:
            recipstr = ' to Multiple Recipients'
        return '%s%s for %s' % (self.amount_str(), recipstr,
                                 self.description)

class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    earmark = models.ForeignKey(Earmark)
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = USStateField()

    def __str__(self):
        return '%s %s %s, %s' % (self.name, self.street, self.city, self.state)

class EarmarkInfo(models.Model):
    earmark = models.ForeignKey(Earmark, primary_key=True)

    views = models.IntegerField(default=0)
    last_view = models.DateTimeField(auto_now=True)

    finished_on = models.DateTimeField(null=True)

    def inc_views(self):
        self.views += 1
        self.save()

class QuestionManager(models.Manager):
    class QuestionAnswer(object):
        def __init__(self, question, answer_id, user_id, answer):
            self.question = question
            self.answer_id = answer_id
            self.user_id = user_id
            self.answer = answer

    def get_with_answers(self, earmark_id):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""SELECT q.id, q.question,
                            a.id, a.user_id, a.answer
                            FROM research_question q LEFT OUTER JOIN
                            research_answer a ON q.id=a.question_id AND
                            a.earmark_id=%s""", [earmark_id])
        res = {}
        for row in cursor.fetchall():
            res[row[0]] = self.QuestionAnswer(*row[1:])
        return res

class Question(models.Model):
    id = models.SlugField(max_length=20, primary_key=True)
    question = models.CharField(max_length=255)

    objects = QuestionManager()

    def __str__(self):
        return self.question

class Answer(models.Model):
    # a user answers a question as it applies to an earmark (at a time)
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    earmark = models.ForeignKey(Earmark)
    answer = models.TextField()

    submit_date = models.DateTimeField(auto_now_add=True, editable=False)

    def get_absolute_url(self):
        return self.earmark.get_absolute_url()

    def __str__(self):
        return self.answer

    class Meta:
        ordering = ['submit_date']

class EarmarkCommentManager(models.Manager):
    def get_query_set(self):
        return super(EarmarkCommentManager, self).get_query_set().filter(type=1)

class UserCommentManager(models.Manager):
    def get_query_set(self):
        return super(UserCommentManager, self).get_query_set().filter(type=2)

class Comment(models.Model):

    EARMARK = 1
    USER = 2
    HELPDESK = 3
    COMMENT_TYPES = (
        (EARMARK, 'Earmark Comment'),
        (USER, 'User Comment'),
        (HELPDESK, 'Helpdesk Comment'),
    )

    user = models.ForeignKey(User)

    type = models.IntegerField(choices=COMMENT_TYPES)
    earmark = models.ForeignKey(Earmark, null=True)
    for_user = models.ForeignKey(User, null=True, related_name='comments_for')

    text = models.TextField()

    submit_date = models.DateTimeField(auto_now_add=True, editable=False)

    objects = models.Manager()
    earmark_comments = EarmarkCommentManager()
    user_comments = UserCommentManager()

    @staticmethod
    def add_comment(type, user, id, text):
        c = Comment(user=user, type=type, text=text)
        if type == Comment.EARMARK:
            c.earmark_id = id
        elif type == Comment.USER:
            c.for_user_id = id
        c.save()
        return c

    def on(self):
        return self.earmark or self.for_user

    def get_absolute_url(self):
        comment_a = '#comment_%s' % self.id
        if self.earmark:
            return self.earmark.get_absolute_url() + comment_a
        else:
            return '/user/%s/messages/%s' % (self.for_user, comment_a)

    def __str__(self):
        return '%s at %s on %s' % (self.user, self.submit_date, self.on())

    class Meta:
        ordering = ['submit_date']


#gatekeeper.register(Answer, import_unmoderated=True)
