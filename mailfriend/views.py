import datetime

from django.shortcuts import render_to_response
from django.http import Http404
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext, loader, Context
from django.conf import settings

from django.contrib.auth.decorators import login_required

# If djano-mailer (http://code.google.com/p/django-mailer/) is available,
# favor it. Otherwise, just use django.core.mail. Thanks to brosner for the
# suggestion (you can also blame him if this doesn't work. Joking. Sort of.)
try:
    from mailer import send_mail
except ImportError:
    from django.core.mail import send_mail

from mailfriend.forms import MailedItemForm
from mailfriend.utils import generic_object_get

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

    try:
        content_type, obj = generic_object_get(int(content_type_id), 
                                               int(object_id))
        obj.get_absolute_url()
    except (ObjectDoesNotExist, AttributeError):
        raise Http404, "Invalid -- the object ID was invalid or does not have a get_absolute_url() method"
    initial_data = {'content_type':content_type.pk, 'object_id':obj.pk}
    form = MailedItemForm(initial=initial_data)
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
    Parses the form and sends the email. (Login required, POST required)

    **Context:**

    ``object``
        The model instance to be mailed.

    **Template**

    mailfriend/sent.html
    
    """
    if not request.POST:
        raise Http404, "Only POSTs are allowed"
    form = MailedItemForm(request.POST)
    try:
        content_type, obj = form.check_generic_object()
    except ObjectDoesNotExist:
        raise Http404, "Object does not exist"
    if form.is_valid():
        mailed_item = form.save(commit=False)
        
        # build full object URL
        site = Site.objects.get_current()
        site_url = 'http://%s/' % site.domain
        url_to_mail = 'http://%s%s' % (site.domain, obj.get_absolute_url())
        
        # render email
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
        
        # send email
        recipient_list = [mailed_item.mailed_to]
        if mailed_item.send_to_user_also:
            recipient_list.append(request.user.email)
        if mailed_item.user_email_as_from:
            from_address = request.user.email
        else:
            from_address = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_address, 
                  recipient_list, fail_silently=False)
        
        # save email to database
        mailed_item.date_mailed = datetime.datetime.now()
        mailed_item.mailed_by = sending_user
        mailed_item.save()
        
        context = Context({ 'object': obj })
        return render_to_response('mailfriend/sent.html', context, 
                                  context_instance=RequestContext(request))
                                  
    # form is invalid
    else:
        return render_to_response('mailfriend/form.html',  {
            'content_type': content_type,
            'form': form,
            'object': obj,
        }, context_instance=RequestContext(request))
  
  
  