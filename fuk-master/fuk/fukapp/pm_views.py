from userena.contrib.umessages.views import MessageDetailListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q

from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from fukapp.forms import PmComposeForm
from .utils import notify_pm_recipients
from userena import settings as userena_settings

# wrappers around the userena messages system to use user ids instead of usernames

@login_required
def pm_message_compose(request, recipients=None, compose_form=PmComposeForm,
                    success_url=None, template_name="umessages/message_form.html",
                    recipient_filter=None, extra_context=None):
    """
    Compose a new message

    :recipients:
        String containing the user ids to send to. Can be
        multiple user id by seperating them with a ``+`` sign.

    :param compose_form:
        The form that is used for getting neccesary information. Defaults to
        :class:`ComposeForm`.

    :param success_url:
        String containing the named url which to redirect to after successfull
        sending a message. Defaults to ``userena_umessages_list`` if there are
        multiple recipients. If there is only one recipient, will redirect to
        ``userena_umessages_detail`` page, showing the conversation.

    :param template_name:
        String containing the name of the template that is used.

    :param recipient_filter:
        A list of :class:`User` that don"t want to receive any messages.

    :param extra_context:
        Dictionary with extra variables supplied to the template.

    **Context**

    ``form``
        The form that is used.

    """
    initial_data = dict()
    user_list = user_objects = []
    if recipients:
        user_list = [r.strip() for r in recipients.split("+")]
        user_objects = User.objects.filter(pk__in=user_list)
        recipient_usernames = [u.username for u in user_objects]
        initial_data["to"] = ", ".join(recipient_usernames)

    if request.method == "GET" and len(user_objects) == 1:
        # redirect if we already have an active conversation.
        to_user = user_objects[0]
        try:
            ctact = MessageContact.objects.get(Q(from_user=request.user, to_user=to_user) |
                               Q(from_user=to_user, to_user=request.user))
        except MessageContact.DoesNotExist:
            pass
        else:
            return redirect(reverse('userena_umessages_detail', args=[user_list[0]]))
    form = compose_form(initial=initial_data)
    if request.method == "POST":
        form = compose_form(request.POST)
        if form.is_valid():
            requested_redirect = request.REQUEST.get("next", False)

            message = form.save(request.user)
            recipients = form.cleaned_data['to']

            if userena_settings.USERENA_USE_MESSAGES:
                messages.success(request, 'Message sent.',
                                 fail_silently=True)

            requested_redirect = request.REQUEST.get(REDIRECT_FIELD_NAME,
                                                     False)

            # notify if requested
            notify_pm_recipients(message)
            # Redirect mechanism            
            redirect_to = reverse('userena_umessages_list')
            if requested_redirect: redirect_to = requested_redirect
            elif success_url: redirect_to = success_url
            elif len(recipients) == 1:
                redirect_to = reverse('userena_umessages_detail',
                                      kwargs={'user_id': recipients[0].id})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context["form"] = form
    extra_context["recipients"] = recipients
    return render(request, template_name, extra_context) 
                              
                              
class PmMessageDetailListView(MessageDetailListView):
    """
    Override the umessages list view to work with our user ids.
    """
    page=1
    paginate_by=10
    template_name='umessages/message_detail.html'
    extra_context=None
    context_object_name = 'message'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PmMessageDetailListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PmMessageDetailListView, self).get_context_data(**kwargs)
        context['recip_id'] = self.recip_id
        context['recip_active'] = self.recipient.is_active
        return context

    def get_queryset(self):
        self.recip_id = self.kwargs['user_id']
        self.recipient = get_object_or_404(User,
                                  pk=self.recip_id)
        queryset = Message.objects.get_conversation_between(self.request.user,
                                                        self.recipient)
        self._update_unread_messages(queryset)
        return queryset



