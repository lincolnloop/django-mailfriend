from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'mailfriend/', include('mailfriend.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
)