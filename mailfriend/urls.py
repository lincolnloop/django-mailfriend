from django.conf.urls.defaults import *

urlpatterns = patterns('mailfriend.views',
    url(r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'mail_item_to_friend_form',
        name='mail_item_to_friend_form'),
    url(r'^send/$',
        'mail_item_to_friend_send',
        name='mail_item_to_friend_send'),
)