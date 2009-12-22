from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models.loading import load_app

from mailfriend.views import mail_item_to_friend_send
from fakeapp.models import FakeItem

class TestMyApp(TestCase):
    urls = 'mailfriend.tests.urls'
    
    def setUp(self):
        # hack to temporarily setup a new app for testing
        # see http://code.djangoproject.com/ticket/7835#comment:21
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS += (
            'mailfriend.tests.fakeapp',
        )
        load_app('mailfriend.tests.fakeapp')
        call_command('syncdb', verbosity=0, interactive=False) #Create tables for fakeapp
        self.fake_item = FakeItem.objects.create(slug="mail-me")
        self.fake_item_ct = ContentType.objects.get_for_model(self.fake_item)
        User.objects.create_user('test', 'test_user@testserver.com', 'test')

    def tearDown(self):
        settings.INSTALLED_APPS = self.old_INSTALLED_APPS

    def test_anonymous_form(self):
        response = self.client.post('/mailfriend/send/', {
                        'content_type':str(self.fake_item_ct.pk),
                        'object_id':str(self.fake_item.pk),
                        'mailed_to':'test@testserver.com',
                        'user_email_as_from':'on',
                        'send_to_user_also':'on',
                })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], 
                         'http://testserver/accounts/login/?next=/mailfriend/send/')
    
    def test_send_to_user(self):
        self.client.login(username='test', password='test')
        response = self.client.post('/mailfriend/send/', {
                         'content_type':str(self.fake_item_ct.pk),
                         'object_id':str(self.fake_item.pk),
                         'mailed_to':'test@testserver.com',
                         'user_email_as_from':'on',
                         'send_to_user_also':'on',
                 })
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'mailfriend/sent.html')
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to,
                          [u'test@testserver.com', u'test_user@testserver.com'])