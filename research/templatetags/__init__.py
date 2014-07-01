from django import template

class TxtNode(template.Node):
    def __init__(self, string):
        self.string = string

    def render(self, context):
        return "%s" % self.string