from django.contrib.auth import login
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from registration.backends import get_backend

# possible view for completing activation - if we can't just redirect to login. 
def activation_complete(request, user, template="registration/activation_complete.html"):
  user.backend = 'registration.backends.default.DefaultBackend'
  login(request, user)
  return render(request, template)

# A copy of django-registration's register method that allows us
# to pass the Request object to the form, so we can run a test on the 
# IP address with StopForumSpam

def register(request, backend, success_url=None, form_class=None,
         disallowed_url='registration_disallowed',
         template_name='registration/registration_form.html',
         extra_context=None):
  backend = get_backend(backend)
  if not backend.registration_allowed(request):
      return redirect(disallowed_url)
  if form_class is None:
      form_class = backend.get_form_class(request)
  
  if request.method == 'POST':
      form = form_class(request, data=request.POST, files=request.FILES)
      if form.is_valid():
          new_user = backend.register(request, **form.cleaned_data)
          if success_url is None:
              to, args, kwargs = backend.post_registration_redirect(request, new_user)
              return redirect(to, *args, **kwargs)
          else:
              return redirect(success_url)
  else:
      form = form_class(request)
  
  if extra_context is None:
      extra_context = {}
  context = RequestContext(request)
  for key, value in extra_context.items():
      context[key] = callable(value) and value() or value
  
  return render_to_response(template_name,
                            { 'form': form },
                            context_instance=context)
