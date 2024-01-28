from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from account.models import Address
from . import cart_module
from product.models import Product
from .cart_module import Cart
from .models import Order, OrderItem, DiscountCode


class CartDetailView(View):
    def get(self, request):
        cart = cart_module.Cart(request)
        return render(request, "cart/cart_detail.html", {'cart': cart})


class CartAddView(View):
    def post(self, request, pk):
        product = Product.objects.get(id=pk)
        size, color, quantity = (request.POST.get("size", 'empty'),
                                 request.POST.get("color", 'empty'), request.POST.get('quantity'))
        cart = cart_module.Cart(request)
        cart.add(product, quantity, color, size)
        return redirect('cart:cart_detail')


class CardDeleteView(View):
    def get(self, request, id):
        cart = Cart(request)
        cart.delete(id)
        return redirect('cart:cart_detail')


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        return render(request, 'cart/order_detail.html', {'order': order})


class OrderCreationView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user, total_price=cart.total())
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                color=item['color'],
                size=item['size'],
                quantity=item['quantity'],
                price=item['price'])
        cart.remove_cart()
        return redirect('cart:order_detail', order.id)


class ApplyDiscountView(LoginRequiredMixin, View):
    def post(self, request, pk):
        code = request.POST.get('discount_code')
        order = get_object_or_404(Order, id=pk)
        discount_code = get_object_or_404(DiscountCode, name=code)
        if discount_code == 0:
            return redirect('cart:order_detail', order.id)

        order.total_price -= order.total_price * discount_code.discount / 100
        order.save()
        discount_code.quantity -= 1
        discount_code.save()
        return redirect('cart:order_detail', order.id)


# ? sandbox merchant
# if settings.SANDBOX:
#     sandbox = 'sandbox'
# else:
#     sandbox = 'www'
#
ZP_API_REQUEST = f"https://api.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://api.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://www.zarinpal.com/pg/StartPay/"
amount = 1000  # Rial / Required
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
phone = 'YOUR_PHONE_NUMBER'  # Optional
# Important: need to edit for realy server.
CallbackURL = 'http://127.0.0.1:8080/cart/verify/'


class SendRequestView(View):
    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        address = get_object_or_404(Address, id=request.POST.get('address'))
        order.address = f'{address.address} - {address.phone} - {address.email}'
        order.save()
        return HttpResponse(request.POST.get('address'))
        # req_data = {
        #     "MerchantID": settings.MERCHANT,
        #     "Amount": order.total_price,
        #     "Description": description,
        #     "Phone": phone,
        #     "CallbackURL": CallbackURL,
        # }
        # data = json.dumps(req_data)
        # # set content length by data
        # headers = {'content-type': 'application/json', 'content-length': str(len(req_data))}
        # try:
        #     response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)
        #
        #     if response.status_code == 200:
        #         response = response.json()
        #         if response['Status'] == 100:
        #             return {'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
        #                     'authority': response['Authority']}
        #         else:
        #             return {'status': False, 'code': str(response['Status'])}
        #     return response
        #
        # except requests.exceptions.Timeout:
        #     return {'status': False, 'code': 'timeout'}
        # except requests.exceptions.ConnectionError:
        #     return {'status': False, 'code': 'connection error'}
