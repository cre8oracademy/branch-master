from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


import uuid


def paypal_subscribe(request):
    """Display the upgrade page. If the user is not logged in, offer them the 
    sign up form."""
    # What you want the button to do.
    # 
    context = {}
    if request.user.is_authenticated():
        custom = request.user.id
        uname = request.user.username
        invoice_id= uuid.uuid4()
        paypal_dict = {
        	"cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "currency_code": "GBP",
            "a3": "10.00", #annual price
            "p3": 1, # duration of each unit
            "t3": "Y", # duration unit
            "src": "1", # make payments recur
            "sra": "1", # reattempt payments on error
            "item_name": "fuk.co.uk Elite Annual Subscription for %s" % uname,
            "invoice": invoice_id,
            "custom": custom,
            "notify_url": "%s%s" % (settings.SITE_NAME, reverse('paypal-ipn')),
            "return_url": "%s%s" % (settings.SITE_NAME, reverse('paypal_success')),
            "cancel_return": "%s%s" % (settings.SITE_NAME, reverse('paypal_cancel')),
        }

        # Create the instance.
        form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")
        context["form"] = form.sandbox()
    return render(request, "fuksubs/paypal_subscribe.html", context)


def paypal_success(request):
    context = {"result": "success"}
    return render(request, "fuksubs/paypal_result.html", context)

def paypal_cancel(request):
    context = {"result": "cancel"}
    return render(request, "fuksubs/paypal_result.html", context)
