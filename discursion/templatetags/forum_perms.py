from django import template

register = template.Library()

class ForumPermNode(template.Node):
    def __init__(self, nodelist, perm, user, obj):
        self.nodelist = nodelist
        self.perm = 'discursion.%s' % perm
        self.user = template.Variable(user)
        self.obj = template.Variable(obj)

    def render(self, context):
        user = self.user.resolve(context)
        obj = self.obj.resolve(context)
        if user.has_perm(self.perm, obj):
            return self.nodelist.render(context)
        return ''

@register.tag
def forumperm(parser, token):
    ''' Usage: {% forumperm create_thread request.user forum %} ... {% endforumperms %}'''
    try:
        tag_name, perm, user, obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%s tag was used wrong.' % token.split_contents()[0])
    nodelist = parser.parse(('endforumperm',))
    parser.delete_first_token()
    return ForumPermNode(nodelist, perm, user, obj)
