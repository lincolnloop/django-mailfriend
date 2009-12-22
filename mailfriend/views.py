import datetime

from django.shortcuts import render_to_response
from django.http import Http404
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext, loader, Context
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# If djano-mailer (http://code.google.com/p/django-mailer/) is available,
# favor it. Otherwise, just use django.core.mail. Thanks to brosner for the
# suggestion (you can also blame him if this doesn't work. Joking. Sort of.)
try:
    from mailer import send_mail
except ImportError:
    from django.core.mail import send_mail

from mailfriend.models import MailedItem
from mailfriend.forms import MailedItemForm

@login_required
def mail_item_to_friend_form(request, content_type_id, object_id):
    """
    Displays the mail item to a friend form. (Login required)

    **Context:**

    ``form``
        The mail item to a friend form.
    ``object``
        The model instance to be mailed.
    ``content_type``
        An instance of :model:`contenttypes.ContentType` for the object.

    **Template**

    mailfriend/form.html
    
    """

    content_type = ContentType.objects.get(pk=content_type_id)
    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
        obj.get_absolute_url()
    except (ObjectDoesNotExist, AttributeError):
        raise Http404, "Invalid -- the object ID was invalid or does not have a get_absolute_url() method"
    form = MailedItemForm()
    context = {
        'content_type': content_type,
        'form': form,
        'object': obj,
    }
    return render_to_response('mailfriend/form.html', 
                              context, context_instance=RequestContext(request))


@login_required
def mail_item_to_friend_send(request):
    """
    Parses the form and sends the email. (Login required)

    **Context:**

    ``object``
        The model instance to be mailed.

    **Template**

    mailfriend/sent.html
    
    """
    if not request.POST:
        raise Http404, "Only POSTs are allowed"
    content_type = ContentType.objects.get(pk=int(request.POST['content_type']))
    try:
        obj = content_type.get_object_for_this_type(
                                            pk=int(request.POST['object_id']))
        obj_url = obj.get_absolute_url()
    except ObjectDoesNotExist:
        raise Http404, "The send to friend form had an invalid 'target' parameter -- the object ID was invalid"
    site = Site.objects.get_current()
    site_url = 'http://%s/' % site.domain
    url_to_mail = 'http://%s%s' % (site.domain, obj_url)
    sending_user = request.user
    subject = "You have received a link"
    message_template = loader.get_template('mailfriend/email_message.txt')
    message_context = Context({ 
        'site': site,
        'site_url': site_url,
        'object': obj,
        'url_to_mail': url_to_mail,
        'sending_user': sending_user,
    })
    message = message_template.render(message_context)
    recipient_list = [request.POST['mailed_to']]
    if request.POST.has_key('send_to_user_also'):
        recipient_list.append(request.user.email)
    if request.POST.has_key('user_email_as_from'):
        from_address = request.user.email
    else:
        from_address = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_address, 
              recipient_list, fail_silently=False)
    mailed_item = MailedItem(date_mailed=datetime.datetime.now(), 
                             mailed_by=sending_user)
    form = MailedItemForm(request.POST, instance=mailed_item)
    form.save()
    context = Context({ 'object': obj })
    return render_to_response('mailfriend/sent.html', context, 
                              context_instance=RequestContext(request))
  
  
  