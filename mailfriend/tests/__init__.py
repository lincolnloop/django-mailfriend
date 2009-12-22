from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase

from mailfriend.models import MailedItem

class MailfriendTest(TestCase):
    urls = 'mailfriend.tests.urls'
    
    def setUp(self):
        self.user = User.objects.create_user('test', 'test_user@testserver.com', 'test')
        self.user_ct = ContentType.objects.get_for_model(self.user)

    def test_form_load(self):
        """Form page loads"""
        self.client.login(username='test', password='test')
        response = self.client.get('/mailfriend/%s/%s/' % (self.user_ct.pk,
                                                           self.user.pk))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'mailfriend/form.html')

    def test_anonymous_send(self):
        """Attempting to send as an anonymous user redirects to login"""
        response = self.client.post('/mailfriend/send/', {
                        'content_type':str(self.user_ct.pk),
                        'object_id':str(self.user.pk),
                        'mailed_to':'test@testserver.com',
                        'user_email_as_from':'on',
                        'send_to_user_also':'on',
                })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], 
                         'http://testserver/accounts/login/?next=/mailfriend/send/')
    
    def test_send_to_user(self):
        """Sends an email and loads the correct page"""
        self.client.login(username='test', password='test')
        response = self.client.post('/mailfriend/send/', {
                         'content_type':str(self.user_ct.pk),
                         'object_id':str(self.user.pk),
                         'mailed_to':'test@testserver.com',
                         'user_email_as_from':'on',
                         'send_to_user_also':'on',
                 })
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'mailfriend/sent.html')
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to,
                          [u'test@testserver.com', u'test_user@testserver.com'])
        mailed_item = MailedItem.objects.all()[0]
        self.assertEquals(mailed_item.mailed_to, 'test@testserver.com')