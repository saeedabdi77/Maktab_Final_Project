from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.generic import ListView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Store, Product, ProductImage, Order, Cart, CartItem
from .forms import AddStoreForm, AddProductForm, ProductImageForm, DefaultImageForm, DateForm
from users.models import Address
from cities_light.models import City, Region
from django.contrib import messages
from django.views.generic.edit import FormView
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


class Home(TemplateView):
    template_name = 'shop-base.html'


class MyStores(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = 'shop-my-stores.html'

    def get(self, request):
        queryset = Store.objects.filter(owner=request.user.seller).order_by('-created_at')
        return render(request, self.template_name, {'stores': queryset})


class AddStore(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    form = AddStoreForm

    def get(self, request, *args, **kwargs):
        return render(request, 'add-store.html', {'form': self.form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            if Store.objects.filter(owner=request.user.seller).filter(status='processing').exists():
                messages.error(request, 'You already have one store processing, you can not register another one!')
                return redirect(reverse('shop-my-stores'))
            form.instance.owner = request.user.seller
            form.instance.status = 'processing'
            province = Region.objects.get(id=form.cleaned_data.get('province'))
            city = City.objects.get(id=form.cleaned_data.get('city'))
            zip_code = form.cleaned_data.get('zip_code')
            address_description = form.cleaned_data.get('address_description')
            address = Address.objects.create(user=request.user, province=province, city=city, zip_code=zip_code,
                                             address_description=address_description)
            form.instance.address = address
            form.save()
            return redirect(reverse('shop-my-stores'))
        return render(request, 'add-store.html', {'form': self.form})


class StoreDetail(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = 'store-detail.html'

    def get(self, request, pk):
        store = Store.objects.get(id=pk)
        if store.status == 'deleted':
            messages.error(request, 'Store not found!')
            return redirect(reverse('shop-my-stores'))
        products = Product.objects.filter(store=store).order_by('-updated_at')
        return render(request, self.template_name, {'store': store, 'products': products})


class DeleteStore(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = 'delete-store.html'

    def get(self, request, pk):
        queryset = Store.objects.get(id=pk)
        return render(request, self.template_name, {'store': queryset})

    def post(self, request, pk):
        store = get_object_or_404(Store, id=pk)
        if store.owner != request.user.seller:
            messages.error(request, 'You don\'t own this store')
            return redirect(reverse('login'))
        store.status = 'deleted'
        store.save()
        return redirect(reverse('shop-my-stores'))


class EditStore(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = 'edit-store.html'
    form = AddStoreForm

    def get(self, request, pk):
        queryset = Store.objects.get(id=pk)
        if queryset.status == 'deleted':
            messages.error(request, 'Store not found!')
            return redirect(reverse('shop-my-stores'))
        self.form = self.form(instance=queryset)
        self.form.fields['zip_code'].initial = queryset.address.zip_code
        self.form.fields['province'].initial = queryset.address.province.pk
        self.form.fields['city'].initial = queryset.address.city.pk
        self.form.fields['address_description'].initial = queryset.address.address_description
        return render(request, self.template_name, {'store': queryset, 'form': self.form})

    def post(self, request, pk):
        form = self.form(request.POST, request.FILES, instance=Store.objects.get(id=pk))
        if form.is_valid():
            if Store.objects.filter(owner=request.user.seller).filter(status='processing').exclude(
                    pk=form.instance.pk).exists():
                messages.error(request, 'You already have one store processing, you can not register another one!')
                return redirect(reverse('shop-my-stores'))
            if form.instance.owner != request.user.seller:
                messages.error(request, 'You don\'t own this store')
                return redirect(reverse('login'))
            form.instance.status = 'processing'
            form.instance.address.province = Region.objects.get(id=form.cleaned_data.get('province'))
            form.instance.address.city = City.objects.get(id=form.cleaned_data.get('city'))
            form.instance.address.zip_code = form.cleaned_data.get('zip_code')
            form.instance.address.address_description = form.cleaned_data.get('address_description')
            form.instance.address.save()
            form.save()
            return redirect(reverse('shop-my-stores'))
        queryset = Store.objects.get(id=pk)
        self.form = self.form(instance=queryset)
        self.form.fields['zip_code'].initial = queryset.address.zip_code
        self.form.fields['province'].initial = queryset.address.province.pk
        self.form.fields['city'].initial = queryset.address.city.pk
        self.form.fields['address_description'].initial = queryset.address.address_description
        return render(request, self.template_name, {'store': queryset, 'form': self.form})


class AddProduct(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = 'add-product.html'
    form = AddProductForm

    def get(self, request, pk):
        queryset = Store.objects.get(id=pk)
        return render(request, self.template_name, {'form': self.form, 'store': queryset})

    def post(self, request, pk):
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            form.instance.store = Store.objects.get(id=pk)
            form.status = 'processing'
            if form.instance.store.owner != request.user.seller:
                messages.error(request, 'You don\'t own this store')
                return redirect(reverse('login'))
            pk = form.save().id
            return redirect(reverse('add-product-image', args=[pk]))


class AddProductImage(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    template_name = 'add-product-image.html'
    form_class = ProductImageForm

    def post(self, request, pk):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('images')
        if form.is_valid():
            for f in files:
                ProductImage.objects.create(image=f, product=Product.objects.get(id=pk))
            return redirect(reverse('default-product-image', args=[pk]))
        else:
            return redirect(reverse('add-product-image', args=[pk]))


class SetDefaultImage(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = 'set-default-image.html'
    form = DefaultImageForm

    def get(self, request, pk):
        return render(request, self.template_name, {'form': self.form})

    def post(self, request, pk):
        if Product.objects.get(id=pk).type:
            return redirect(reverse('add-product-field', args=[pk]))
        else:
            return redirect(reverse('store-detail', args=[Product.objects.get(id=pk).store.id]))


class StoreOrder(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = 'store-orders.html'
    form = DateForm

    def get(self, request, pk):
        cart_items = CartItem.objects.filter(product__store=Store.objects.get(id=pk))
        carts = []
        for cart_item in cart_items:
            carts.append(Cart.objects.get(cartitem=cart_item))
        orders = []
        for cart in carts:
            if (Order.objects.filter(cart=cart).exists()) and (Order.objects.get(cart=cart) not in orders):
                orders.append(Order.objects.get(cart=cart))
        orders.sort(key=lambda x: x.cart.updated_at, reverse=True)
        return render(request, self.template_name, {'form': self.form, 'orders': orders})

    def post(self, request, pk):
        if request.POST.get('date'):
            date = datetime.strptime(request.POST.get('date')[:-3], '%m/%d/%Y %H:%M').date()
            cart_items = CartItem.objects.filter(product__store=Store.objects.get(id=pk))
            carts = []
            for cart_item in cart_items:
                if Cart.objects.filter(updated_at__date=date).filter(cartitem=cart_item).exists():
                    carts.append(Cart.objects.filter(updated_at__date=date).get(cartitem=cart_item))
            orders = []
            for cart in carts:
                if (Order.objects.filter(cart=cart).exists()) and (Order.objects.get(cart=cart) not in orders):
                    orders.append(Order.objects.get(cart=cart))
            orders.sort(key=lambda x: x.cart.updated_at, reverse=True)
            return render(request, self.template_name, {'form': self.form, 'orders': orders})

        if request.POST.get('filter'):
            status = request.POST.get('filter')
            cart_items = CartItem.objects.filter(product__store=Store.objects.get(id=pk))
            carts = []
            for cart_item in cart_items:
                carts.append(Cart.objects.get(cartitem=cart_item))
            orders = []
            for cart in carts:
                if (Order.objects.filter(cart=cart).exists()) and (
                        Order.objects.get(cart=cart) not in orders) and (Order.objects.get(cart=cart).status == status):
                    orders.append(Order.objects.get(cart=cart))
            orders.sort(key=lambda x: x.cart.updated_at, reverse=True)
            return render(request, self.template_name, {'form': self.form, 'orders': orders})

        action = request.POST.get('action')
        order_id = int(action[0])
        status = action[2:]

        order = Order.objects.get(id=order_id)
        if status == 'info':
            cart_items = CartItem.objects.filter(cart__order=order)
            return render(request, 'order-detail.html', {'cart_items': cart_items, 'pk': pk})

        Order.objects.filter(id=order_id).update(status=status)

        subject = f"order on ONLINE STORE"
        message = f'your order at {order.cart.updated_at} is {status}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [order.cart.buyer.email]
        send_mail(subject, message, email_from, recipient_list)

        cart_items = CartItem.objects.filter(product__store=Store.objects.get(id=pk))
        carts = []
        for cart_item in cart_items:
            carts.append(Cart.objects.get(cartitem=cart_item))
        orders = []
        for cart in carts:
            if (Order.objects.filter(cart=cart).exists()) and (Order.objects.get(cart=cart) not in orders):
                orders.append(Order.objects.get(cart=cart))
        orders.sort(key=lambda x: x.cart.updated_at, reverse=True)
        return render(request, self.template_name, {'form': self.form, 'orders': orders})
