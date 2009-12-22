from django.conf.urls.defaults import *

from mailfriend.views import *

urlpatterns = patterns('',
  url(
    regex   = '^(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
    view    = mail_item_to_friend_form,
    name    = 'mail_item_to_friend_form',
  ),
  url(
    regex   = '^send/$',
    view    = mail_item_to_friend_send,
    name    = 'mail_item_to_friend_send',
  ),
)