from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def get_mail_to_friend_url(obj):
  """
  Given an object, returns the URL for its "mail to friend" URL. The object
  must have a get_absolute_url method. If it does not, this template tag
  will fail silently.
  """
  if hasattr(obj, 'get_absolute_url'):
    try:
      content_type = ContentType.objects.get(app_label=obj._meta.app_label, model=obj._meta.module_name)
      return reverse('mailfriend.views.mail_item_to_friend_form', args=[ content_type.id, obj.id ])
    except:
      return ''
  else:
    return ''
  