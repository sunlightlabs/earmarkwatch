from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage

from django.contrib.auth.models import User
from earmarkwatch.users.models import UserProfile
from earmarkwatch.research.models import Earmark, Comment

from earmarkwatch.users.forms import UserProfileForm
from sharedauth.forms import ChangePasswordForm

def user_comments(user):
    comments = user.comment_set.filter(type=Comment.EARMARK).order_by('-submit_date')
    seen_earmarks = set()
    return_set = []
    for c in comments:
        if c.earmark_id not in seen_earmarks:
            return_set.append(c)
            seen_earmarks.add(c.earmark_id)
    return return_set

def user_view(request, username, tab='profile', page_num=None):

    #tab should be one of: comments,messages,research

    user = get_object_or_404(User, username=username)
    context = {'the_user':user, 'tab': tab}
    paginator = None

    if tab == 'profile':
        if request.user.id == user.id:
            context['new_comments'] = user.comments_for.filter(
                submit_date__gt=user.last_login).count()

        commented = user.comment_set.filter(type=Comment.EARMARK).values('earmark').distinct()
        user.comment_count = len(commented)
        research_count = Earmark.objects.researched_by(user.id).values('appropriated').distinct()
        user.researched_count = len(research_count)
        appropriated = Earmark.objects.researched_by(user.id).values('appropriated')
        user.research_sum = sum([e['appropriated'] for e in appropriated])
        user.researched = Earmark.objects.researched_by(user.id)[0:1]
        user.comments = user_comments(user)[0:3]

        template = 'user.html'

    elif tab == 'earmarks':
        # paginate earmarks researched by user
        paginator = Paginator(Earmark.objects.researched_by(user.id), 5)
    elif tab == 'comments':
        # paginate comments posted by user
        paginator = Paginator(user_comments(user), 5)
    elif tab == 'messages':
        paginator = Paginator(user.comments_for.order_by('-submit_date'), 5)
    elif tab == 'manage':
        context['change_password_form'] = ChangePasswordForm()
        profile,created = UserProfile.objects.get_or_create(user=request.user)
        if created:
            pform = UserProfileForm()
        else:
            pform = UserProfileForm({ 'about': profile.about})
        context['profile_form'] = pform

    template = 'user_%s.html' % tab

    if paginator:
        if not page_num:
            page_num = 1
        else:
            page_num = int(page_num)
        context['prev_url'] = '%s%s/%s' % (reverse('user_view', args=[username]), tab, page_num-1)
        context['next_url'] = '%s%s/%s' % (reverse('user_view', args=[username]), tab, page_num+1)
        context['page'] = paginator.page(page_num)

    return render_to_response(template, context,
                              context_instance=RequestContext(request))


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        profile = UserProfile.objects.get(user=request.user)
        if form.is_valid():
            profile.about = form.cleaned_data['about']
            profile.save()
    return HttpResponseRedirect(reverse('user_view',
                                        args=[request.user.username]) +
                                'manage/')
