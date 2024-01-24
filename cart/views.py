from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from . import cart_module
from product.models import Product
from .cart_module import Cart
from .models import Order, OrderItem


class CartDetailView(View):
    def get(self, request):
        cart = cart_module.Cart(request)
        return render(request, "cart/cart_detail.html", {'cart': cart})


class CartAddView(View):
    def post(self, request, pk):
        product = Product.objects.get(id=pk)
        size, color, quantity = request.POST.get("size", 'empty'), request.POST.get("color", 'empty'), request.POST.get(
            'quantity')
        cart = cart_module.Cart(request)
        cart.add(product, quantity, color, size)
        return redirect('cart:cart_detail')


class CardDeleteView(View):
    def get(self, request, id):
        cart = Cart(request)
        cart.delete(id)
        return redirect('cart:cart_detail')


class OrderDetailView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        return render(request, 'cart/order_detail.html', {'order':order})


class OrderCreationView(View):
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

        return redirect('cart:order_detail', order.id)