from django import template
from django.template import resolve_variable

from earmarkwatch.research.models import Answer
import gatekeeper

register = template.Library()

@register.tag
def flag_answer(parser, token):
    try:
        # {% show_flag_for questions.website %}
        tag_name, question = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return FlagNode(question)

class FlagNode(template.Node):
    def __init__(self, question):
        self.question = question

    def render(self, context):
        try:
            ans_id = resolve_variable(self.question+'.answer_id', context)
            logged_in = resolve_variable('user.is_authenticated', context)
            answer = Answer.objects.get(pk=ans_id)
            #if not logged_in or answer.moderation_status == gatekeeper.APPROVED_STATUS:
                return ''
            elif answer.flagged:
                return '<sup id="flagquestion%s" class="flagged">flagged</sup>' % ans_id
            else:
                return '<sup id="flagquestion%s"><a href="javascript:flagAnswer(%s);" class="flag">(Flag)</a></sup>' % (ans_id, ans_id)
        except template.VariableDoesNotExist:
            return ''
