
from django.shortcuts import render
from django.conf import settings


from django.http import JsonResponse
from .models import Invoice

import stripe
import uuid
import json

stripe.api_key = settings.STRIPE_SECRET_KEY
# stripe.ApplePayDomain.create(
#   domain_name='example.com',
# )

# def payment_gateways(request):
# 	print(settings.STRIPE_PUBLISHABLE_KEY)
# 	context = {
# 		'key': settings.STRIPE_PUBLISHABLE_KEY
# 	}
# 	return render(request, 'payments/payment_gateways.html', context)


def payment_paypal(request):
	return render(request, 'payments/paypal.html', context={})


def payment_stripe(request):
	return render(request, 'payments/stripe.html', context={})


def payment_coinbase(request):
	return render(request, 'payments/coinbase.html', context={})


def payment_paylike(request):
	return render(request, 'payments/paylike.html', context={})


def payment_succeed(request):
	return render(request, 'payments/payment_succeed.html', context={})


# def charge(request):
# 	if request.method == 'POST':
# 		charge = stripe.Charge.create(
# 			amount=500,
# 			currency='eur',
# 			description='Payment GetWays',
# 			source=request.POST['stripeToken']
# 		)
# 		return render(request, 'payments/charge.html')




from django.shortcuts import redirect
from django.views.generic.base import TemplateView

class PaymentGetwaysView(TemplateView):
    template_name = 'payments/payment_gateways.html'

    def get_context_data(self, **kwargs): # new
        context = super(PaymentGetwaysView, self).get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['amount'] = 500
        context['description'] = "Stripe Payment"
        context['invoice_session'] = self.request.session['invoice_session']
        print(context['invoice_session'])
        return context



def charge(request): # new
    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount=500,
            currency='eur',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        invoice_code = request.session['invoice_session']
        invoice = Invoice.objects.get(invoice_code=invoice_code)
        invoice.payment_complete = True
        invoice.save()
        return redirect('completed')
        # return JsonResponse({"invoice_code": invoice.invoice_code}, status=201)
        # return render(request, 'payments/charge.html')


def create_invoice(request):
    print(request.is_ajax())
    if request.method == 'POST':
        invoice = Invoice.objects.create(
            user = request.user,
            amount = request.POST.get('amount'),
            total=26,
            invoice_code=str(uuid.uuid4()),
        )
        request.session['invoice_session'] = invoice.invoice_code
        return redirect('payment_gateways')
    # if request.is_ajax():
    #     invoice = Invoice.objects.create(
    #         user = request.user,
    #         amount = 15,
    #         total=26,
    #     )
    #     return JsonResponse({'invoice': invoice}, status=201) # created

    return render(request, 'invoices.html', context={
        'invoices': Invoice.objects.filter(user=request.user)
    })


def invoice_detail(request, slug):
    return render(request, 'invoice_detail.html', context={
        'invoice': Invoice.objects.get(invoice_code=slug)
    })


def paymentComplete(request):
    print(request.is_ajax())
    if request.is_ajax() or request.method == 'POST':
        invoice_id = request.session['invoice_session']
        invoice = Invoice.objects.get(id=invoice_id)
        invoice.payment_complete = True
        invoice.save()
        # return redirect('invoice', invoice.invoice_code)
    body = json.loads(request.body)
    print('BODY:', body)
    return JsonResponse('Payment completed!', safe=False)


from django.http import JsonResponse

import gopay
from gopay.enums import Recurrence, PaymentInstrument, BankSwiftCode, Currency, Language


def gopay_payment(request):
    print("\nrequest \n", request.method)
    # api = gopay.payments({
    #     'goid': '8302931681',
    #     'clientId': '1061399163',
    #     'clientSecret': 'stDTmVXF',
    #     'isProductionMode': False,
    #     'scope': gopay.TokenScope.ALL,
    #     'language': gopay.Language.ENGLISH,
    #     'timeout': 30
    # })
    # # token is retrieved automatically, you don't have to call some method `get_token`

    # response = api.get_status('3000006542')
    # if response.has_succeed():
    #     print("hooray, API returned " + str(response))
    # else:
    #     print("oops, API returned " + str(response.status_code) + ": " + str(response))

    # payments = gopay.payments({
    #     'goid': 'my goid',
    #     'clientId': 'my id',
    #     'clientSecret': 'my secret',
    #     'isProductionMode': False
    # })
    if request.method == 'POST':
        user = request.user

        payments = gopay.payments({
            'goid': '8302931681',
            'clientId': '1061399163',
            'clientSecret': 'stDTmVXF',
            'isProductionMode': False,
            'scope': gopay.TokenScope.ALL,
            'language': gopay.Language.ENGLISH,
            'timeout': 30
        })

        # recurrent payment must have field ''
        recurrentPayment = {
            'recurrence': {
                'recurrence_cycle': Recurrence.DAILY,
                'recurrence_period': "7",
                'recurrence_date_to': '2015-12-31'
            }
        }

        # pre-authorized payment must have field 'preauthorization'
        preauthorizedPayment = {
            'preauthorization': True
        }

        response = payments.create_payment({
            'payer': {
                'default_payment_instrument': PaymentInstrument.BANK_ACCOUNT,
                'allowed_payment_instruments': [PaymentInstrument.BANK_ACCOUNT],
                'default_swift': BankSwiftCode.FIO_BANKA,
                'allowed_swifts': [BankSwiftCode.FIO_BANKA, BankSwiftCode.MBANK],
                'contact': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone_number': user.phone,
                    'city': 'example city',
                    'street': 'Plana 67',
                    'postal_code': '373 01',
                    'country_code': 'CZE',
                },
                # 'contact': {
                #     'first_name': 'Zbynek',
                #     'last_name': 'Zak',
                #     'email': 'zbynek.zak@gopay.cz',
                #     'phone_number': '+420777456123',
                #     'city': 'C.Budejovice',
                #     'street': 'Plana 67',
                #     'postal_code': '373 01',
                #     'country_code': 'CZE',
                # },
            },
            'amount': 150,
            'currency': Currency.CZECH_CROWNS,
            'order_number': '001',
            'order_description': 'pojisteni01',
            'items': [
                {'name': 'item01', 'amount': 50},
                {'name': 'item02', 'amount': 100},
            ],
            'additional_params': [
                {'name': 'invoicenumber', 'value': '2015001003'}
            ],
            'callback': {
                'return_url': 'http://www.your-url.tld/return',
                'notification_url': 'http://www.your-url.tld/notify'
            },
            'lang': Language.CZECH,  # if lang is not specified, then default lang is used
        })

        if response.has_succeed():
            print("\nPayment Succeed\n")
            print("hooray, API returned " + str(response))
        else:
            print("\nPayment Fail\n")
            print("oops, API returned " + str(response.status_code) + ": " + str(response))
        return JsonResponse({"message": str(response)})
            
    return JsonResponse({"message": "GET requested"})