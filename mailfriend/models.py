import datetime

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class MailedItem(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey()
    mailed_by = models.ForeignKey(User)
    mailed_to = models.EmailField()
    user_email_as_from = models.BooleanField(default=False)
    send_to_user_also = models.BooleanField(default=False)
    date_mailed = models.DateTimeField(default=datetime.datetime.now, editable=False)

    def __unicode__(self):
        return "%s: To %s, from %s" % (unicode(self.content_object), 
                                       self.mailed_to, 
                                       unicode(self.mailed_by))
