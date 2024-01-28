
from django.shortcuts import render
from django.views.generic import DetailView, TemplateView, ListView
from product.models import Product, Category


class ProductDetailView(DetailView):
    template_name = 'product/product_detail.html'
    model = Product


class NavbarPartialView(TemplateView):
    template_name = 'include/navbar.html'

    def get_context_data(self, **kwargs):
        context = super(NavbarPartialView, self).get_context_data()
        context['categories'] = Category.objects.all()
        return context


class CategoryStyle(TemplateView):
    template_name = 'include/category.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryStyle, self).get_context_data()
        context['categories'] = Category.objects.all()
        return context


class ProductListView(ListView):
    template_name = 'product/products_list.html'
    queryset = Product.objects.all()

    def get_context_data(self, **kwargs):
        request = self.request
        colors = request.GET.getlist('color')
        sizes = request.GET.getlist('size')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        queryset = Product.objects.all()
        if colors:
            queryset = queryset.filter(color__title__in=colors).distinct()
        if sizes:
            queryset = queryset.filter(size__title__in=sizes).distinct()
        if min_price and max_price:
            queryset = queryset.filter(price__lte=max_price, price__gte=min_price)
        context = super(ProductListView, self).get_context_data()
        context['object_list'] = queryset
        return context




