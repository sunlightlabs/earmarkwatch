from django import template
from earmarkwatch.research.templatetags import TxtNode

register = template.Library()

@register.tag
def total_researched(parser, token):
	from django.db import connection
	cursor = connection.cursor()
	cursor.execute('''SELECT DISTINCT earmark_id FROM research_answer''')
	total_research_number = cursor.rowcount
	return TxtNode(total_research_number)
	
