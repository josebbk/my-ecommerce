from .models import *
import stripe
import string
import random
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect


# def get_customer(request):
#     if request.user.is_authenticated:
#         customer = Customer.objects.get(user=request.user)
#         return customer
#     else:
#         # get device cookie if it's a guest
#         # TODO: if the person enters th site for the first time, it demands a cookie while it hasn't been created
#         try:
#             device = request.COOKIES['device']
#         except KeyError:
#             device = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
#             # response = HttpResponseRedirect('/')
#             # code = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
#             # response.set_cookie('device', code)
#             # return response
#
#         customer, created = Customer.objects.get_or_create(device_code=device)
#         return customer


# create reference code for the orders that took place (payment_charge_post)
def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


# stripe test api
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"


# for payment.view
def payment_charge_post(request, customer, order, token, amount):
    try:
        # Use Stripe's library to make requests...
        charge = stripe.Charge.create(
            amount=amount,  # cents
            currency="usd",
            source=token,
        )

        # Create The Payment
        payment = Payment(
            stripe_charge_id=charge['id'],
            amount=order.get_total(),
            customer=customer,
        )
        payment.save()

        # Assign the payment to the order
        order.order_complete = True
        order.payment = payment
        # Create Ref Code
        order.ref_code = create_ref_code()
        order.save()
        # OrderItem Model Update To Complete
        order_item = OrderItem.objects.filter(customer=customer, order_complete=False).all()
        for item in order_item:
            item.order_complete = True
            item.save()

        messages.info(request, 'Your Order Was Successful')
        pass

    except stripe.error.CardError as e:
        body = e.json_body
        err = body.get('error', {})
        messages.warning(request, "{}".format(err.get('message')))
        return 'error'

    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        messages.warning(request, "Rate Limit Error")
        return 'error'
        pass
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        messages.warning(request, 'Invalid Parameters')
        return 'error'
        pass
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        messages.warning(request, 'Not Authenticated')
        return 'error'
        pass
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        messages.warning(request, 'Network Error')
        return 'error'
        pass
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        messages.warning(request, 'Something went wrong you were not charged. please try again.')
        return 'error'
        pass
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        # send email to ourselves
        messages.warning(request, 'a serious error occurred. we have been notified.')
        return 'error'
        pass


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        return None
