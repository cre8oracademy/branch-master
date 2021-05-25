from django.conf.urls import *
from registration.views import activate
from registration_app.views import register, activation_complete
from django.views.generic import TemplateView
from django.contrib.auth.views import password_change, password_change_done
from django.contrib.auth.views import password_reset, password_reset_complete, password_reset_confirm, password_reset_done
from registration_app.forms import RecaptchaRegistrationForm

# url patterns copied in from django registration so  that we can add extra stuff in to the views.

urlpatterns = patterns('',
    url(r'^register/$', register,
        {'form_class': RecaptchaRegistrationForm, 'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_register'),
    url(r'^activate/complete/$',
      TemplateView.as_view(template_name='registration/activation_complete.html'),
      name='registration_activation_complete'),
   # Activation keys get matched by \w+ instead of the more specific
   # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
   # that way it can return a sensible "invalid key" message instead of a
   # confusing 404.
   url(r'^activate/(?P<activation_key>\w+)/$',
       activate,
       { 'backend': 'registration.backends.default.DefaultBackend', 'success_url': '/' },
       name='registration_activate'),
   url(r'^register/complete/$',
       TemplateView.as_view(template_name='registration/registration_complete.html'),
       name='registration_complete'),
   url(r'^register/closed/$',
       TemplateView.as_view(template_name='registration/registration_closed.html'),
       name='registration_disallowed'),
     (r'', include('registration.auth_urls')),
   

)

