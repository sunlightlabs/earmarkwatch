from datetime import datetime
from math import floor

from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse

from earmarkwatch.research.models import *
from earmarkwatch.research.forms import SearchForm, STATE_LOOKUP

def index(request):
    context = {
        'comments': Comment.earmark_comments.order_by('-submit_date')[:3],
        'earmarks': Earmark.objects.order_by_lastmodified()[:5],
        'random': Earmark.objects.order_by_virgin()[:1]
    }
    if request.user.is_authenticated():
        context['researched'] = Earmark.objects.researched_by(request.user.id).count()
        appropriated = Earmark.objects.researched_by(request.user.id).values('appropriated')
        context['research_sum'] = sum([earmark['appropriated'] for earmark in appropriated])
        context['commented_on'] = len(Comment.objects.filter(user=request.user.id, type=Comment.EARMARK).values('earmark').distinct())
    return render_to_response('index.html', context,
                              context_instance=RequestContext(request))

def faq(request):
    return render_to_response('faq.html',
                              context_instance=RequestContext(request))

def mapped(request):
    return render_to_response('mapped.html',
                              context_instance=RequestContext(request))


def recent_research(request):
    context = {
        'earmarks': Earmark.objects.order_by_lastmodified()[:25]
    }
    return render_to_response('recent_research.html', context,
                              context_instance=RequestContext(request))

def most_comments(request):
    context = {
        'earmarks': Earmark.objects.order_by_mostcomments()[:15]
    }
    return render_to_response('most_comments.html', context,
                              context_instance=RequestContext(request))

def recent_comments(request, year=None, chamber=None, bill=None):
    comments = Comment.earmark_comments.order_by('-submit_date')
    earmarks = Earmark.objects.order_by_popularity()
    context = dict()

    context['comments'] = comments[:15]
    return render_to_response('recent_comments.html', context,
                              context_instance=RequestContext(request))


def active(request, year=None, chamber=None, bill=None):
    comments = Comment.earmark_comments.all()
    earmarks = Earmark.objects.order_by_virgin()
    context = dict()

    if year and chamber and bill:
        source = get_object_or_404(Source, year=year, chamber=chamber, type=bill)
        comments = comments.filter(earmark__source=source)
        earmarks = earmarks.filter(source=source)
        context['source'] = source

    context['comments'] = comments[:1]
    context['earmarks'] = earmarks[:10]
    return render_to_response('active.html', context,
                              context_instance=RequestContext(request))

def search(request, year=None, chamber=None, bill=None):
    earmarks = None
    source = None
    context = dict()

    state = request.GET.get('state')
    sponsor = request.GET.get('sponsor')
    text = request.GET.get('text')
    recip = request.GET.get('recipient')

    if year and chamber and bill:
        source = get_object_or_404(Source, year=year, chamber=chamber, type=bill)
        context['source'] = source
        form = SearchForm(request.GET)
        if chamber == 'house':
            qs = form.fields['sponsor'].queryset.filter(title='Rep')
        else:
            qs = form.fields['sponsor'].queryset.filter(title='Sen')
        form.fields['sponsor'].queryset = qs
        context['form'] = form

    if state or sponsor or text or recip:
        if source:
            earmarks = Earmark.objects.filter(source=source)
        else:
            earmarks = Earmark.objects.all()

    context['tab'] = 'state'
    if state:
        earmarks = earmarks.filter(location__state=state)
        context['search_term'] = STATE_LOOKUP[state]
        context['tab'] = 'tab1'
    elif sponsor:
        earmarks = earmarks.filter(sponsors__pk=sponsor)
        context['search_term'] = str(Politician.objects.get(pk=sponsor))
        context['tab'] = 'sponsor'
    elif text:
        earmarks = earmarks.extra(where=['MATCH(description) AGAINST ("%s")'],
                                  params=[text])
        context['search_term'] = text
        context['tab'] = 'description'
    elif recip:
        earmarks = earmarks.extra(tables=['research_location'],
                                  where=['MATCH(research_location.name) AGAINST("%s")',
                                         'research_location.earmark_id=research_earmark.id'],
                                  params=[recip])
        context['search_term'] = recip
        context['tab'] = 'recipient'

    context['recipients'] = [str(l['name']) for
                             l in Location.objects.filter(
                                earmark__source__id=source.id).values('name').distinct()]

    if earmarks:
        context['earmarks'] = earmarks
        context['total'] = sum([e.appropriated for e in earmarks])

    return render_to_response('search.html', context,
                              context_instance=RequestContext(request))

def random_earmark(request, year, chamber, bill):
    # grabs a random earmark (TODO: filter completed earmarks)
    source = get_object_or_404(Source, year=year, chamber=chamber, type=bill)
    earmark = Earmark.objects.filter(source=source).order_by('?')[0]
    return HttpResponseRedirect(reverse('earmark_view', args=[earmark.id]))

def earmark_view(request, eid=None):
    if request.method == 'POST' and request.user.is_authenticated():
        eid = int(request.POST['eid'])
        for k,v in request.POST.items():
            if v and k != 'eid':
                try:
                    ans = Answer.objects.get(question__id=k, earmark__id=eid)
                    if ans.user == request.user:
                        ans.user = request.user
                        ans.answer = v
                        ans.save()
                except Answer.DoesNotExist:
                    ans = Answer(user=request.user, question_id=k, 
                                 earmark_id=eid, answer=v)
                ans.save()

        einfo = EarmarkInfo.objects.get(earmark__id=eid)

        # if #questions equals #answered, this earmark is complete
        questions = Question.objects.count()
        answered = Answer.objects.filter(earmark__id=eid).count()
        if questions == answered:
            einfo.finished_on = datetime.now()
        else:   # needed if deleted info made earmark uncomplete
            einfo.finished_on = None

        einfo.save()

        return HttpResponseRedirect(reverse('earmark_view', args=[eid]))
    else:
        welcome = not request.session.get('seen_earmarks_page', False)
        request.session['seen_earmarks_page'] = True

        earmark = get_object_or_404(Earmark, id=eid)

        einfo,created = EarmarkInfo.objects.get_or_create(earmark=earmark)
        einfo.inc_views()

        questions = Question.objects.get_with_answers(eid)
        no_research = True
        any_editable = False
        contributors = set()
        for q in questions.values():
            contributors.add(q.user_id)
            q.editable = (q.answer is None or
                          q.user_id == request.user.id)
            any_editable = any_editable or q.editable
            no_research = no_research and (q.answer is None)
            if q.answer is None:
                q.answer = ''
        comments = earmark.comment_set.all()
        contributors = User.objects.in_bulk(list(contributors)).values()
        if contributors:
            contributors[-1].last = True    # hack for output

        if earmark.location_set.count() == 1:
            earmark.location = earmark.location_set.all()[0]

        context = {'earmark': earmark, 'source': earmark.source,
                   'questions': questions, 'contributors': contributors,
                   'comments': comments, 'no_research': no_research,
                   'any_editable': any_editable, 'welcome': welcome,
                   'next_path': '?next='+request.path}
        return render_to_response('view_earmark.html', context,
                                  context_instance=RequestContext(request))

def sponsor_view(request, year, chamber, bill, id):

    sponsor = Politician.objects.get(pk=id)
    source = get_object_or_404(Source, year=year, chamber=chamber, type=bill)
    earmarks = sponsor.earmark_set.filter(source=source)
    amount, rank = sponsor.calc_earmark_total(source.id)
    if chamber=='house':
        peers = 435
    else:
        peers = 100

    percentile = floor(100*((float)(peers-rank)/peers))

    return render_to_response('sponsor.html', {'sponsor': sponsor,
                                               'source': source,
                                               'earmarks': earmarks,
                                               'amount': amount,
                                               'percentile': percentile},
                              context_instance=RequestContext(request))

@require_POST
@login_required
def post_comment(request, type):
    id = int(request.POST['id'])
    text = request.POST['text']

    c = Comment.add_comment(type, request.user, id, text)

    if type == Comment.EARMARK:
        return HttpResponseRedirect('%s#comment_%s' % (
                                   reverse('earmark_view', args=[id]),
                                   c.id))
    elif type == Comment.USER:
        return HttpResponseRedirect('%smessages/#comment_%s' %
            (reverse('user_view', args=[c.for_user.username]), c.id))

@require_POST
@login_required
def flag(request, id, type):
    obj = get_object_or_404(type, pk=int(id))
    obj.moderation_object.flag(request.user)
    return HttpResponse("flagged")

@require_POST
@login_required
def flag_answers_for(request, earmark_id):
    answers = get_list_or_404(Answer, earmark=earmark_id)
    ans_ids = []
    for ans in answers:
        ans_ids.append(str(ans.id))
        ans.moderation_object.flag(request.user)
    return HttpResponse('[' + ','.join(ans_ids) + ']')
