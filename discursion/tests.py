from django.conf import settings
from django.test import TestCase

class DiscursionTests(TestCase):
    def test_markup_renderers(self):
        ''' Test that the markup renderers work '''
        from discursion.render_backends import get_render_backend
        path = 'discursion.render_backends.%s'

        render = get_render_backend(path % 'Simple')
        self.assertEqual(render('http://www.dmpayton.com'), '<a href="http://www.dmpayton.com" rel="nofollow">http://www.dmpayton.com</a>')

        render = get_render_backend(path % 'BBCode')
        self.assertEqual(render('[b]Discursion[/b]'), '<strong>Discursion</strong>')

        render = get_render_backend(path % 'Markdown')
        self.assertEqual(render('**Discursion**'), '<p><strong>Discursion</strong></p>')

        render = get_render_backend(path % 'Textile')
        self.assertEqual(render('*Discursion*'), '<p><strong>Discursion</strong></p>')

        render = get_render_backend(path % 'ReStructuredText')
        self.assertEqual(render('**Discursion**'), '<p><strong>Discursion</strong></p>')
