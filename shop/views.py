from django.shortcuts import render, reverse, redirect, get_object_or_404, HttpResponseRedirect
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import UpdateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Store, Product, ProductImage, Order, Cart, CartItem, ProductDetail, ProductField
from .forms import AddStoreForm, AddProductForm, DateForm, ProductFieldsForm
from users.models import Address, CustomUser
from cities_light.models import City, Region
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.db.models import Sum, F, Count
from .permissions import IsStoreOwner, IsProductOwner, IsSeller


class Home(IsSeller, TemplateView):
    template_name = 'shop-home.html'


class MyStores(LoginRequiredMixin, IsSeller, View):
    login_url = '/accounts/login/'
    template_name = 'shop-my-stores.html'

    def get(self, request):
        queryset = Store.objects.filter(owner=request.user.seller).order_by('-created_at')
        return render(request, self.template_name, {'stores': queryset})


class AddStore(LoginRequiredMixin, IsSeller, View):
    login_url = '/accounts/login/'
    form = AddStoreForm

    def get(self, request):
        return render(request, 'add-store.html', {'form': self.form})

    def post(self, request):
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


class StoreDetail(LoginRequiredMixin, IsSeller, IsStoreOwner, View):
    login_url = '/accounts/login/'
    template_name = 'store-detail.html'

    def get(self, request, pk):
        store = Store.objects.get(id=pk)
        if store.status == 'deleted':
            messages.error(request, 'Store not found!')
            return redirect(reverse('shop-my-stores'))
        products = Product.objects.filter(store=store).order_by('-updated_at')
        return render(request, self.template_name, {'store': store, 'products': products})


class DeleteStore(LoginRequiredMixin, IsSeller, IsStoreOwner, View):
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


class EditStore(LoginRequiredMixin, IsSeller, IsStoreOwner, View):
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


class AddProduct(LoginRequiredMixin, IsSeller, IsStoreOwner, View):
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
            form.instance.status = 'processing'
            if form.instance.store.owner != request.user.seller:
                messages.error(request, 'You don\'t own this store')
                return redirect(reverse('login'))
            pk = form.save().id
            files = request.FILES.getlist('images')
            for f in files:
                ProductImage.objects.create(image=f, product=Product.objects.get(id=pk))
            return redirect(reverse('default-product-image', args=[pk]))


class SetDefaultImage(LoginRequiredMixin, IsSeller, View):
    login_url = '/accounts/login/'
    template_name = 'set-default-image.html'

    def get(self, request, pk):
        images = ProductImage.objects.filter(product=Product.objects.get(id=pk))
        return render(request, self.template_name, {'images': images})

    def post(self, request, pk):
        product = Product.objects.get(id=pk)
        instance = ProductImage.objects.filter(product=product)[int(request.POST.get('default')) - 1]
        instance.default = True
        instance.save()
        if Product.objects.get(id=pk).type:
            return redirect(reverse('set-product-fields', args=[pk]))
        else:
            return redirect(reverse('store-detail', args=[product.store.id]))


class AddProductFields(LoginRequiredMixin, IsSeller, View):
    login_url = '/accounts/login/'
    template_name = 'add-product-field.html'
    form = ProductFieldsForm

    def get(self, request, pk):
        type = Product.objects.get(id=pk).type
        keys = type.details.all()
        form = self.form(keys)
        return render(request, self.template_name, {'form': form, 'pk': pk})

    def post(self, request, pk):
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            product = Product.objects.get(id=pk)
            key = ProductField.objects.get(name=key)
            ProductDetail.objects.create(product=product, key=key, value=value)
        return redirect(reverse('store-detail', args=[Product.objects.get(id=pk).store.id]))


class EditProduct(LoginRequiredMixin, IsSeller, IsProductOwner, UpdateView):
    login_url = '/accounts/login/'
    template_name = 'edit-product.html'
    model = Product
    fields = ['price', 'quantity']

    def form_valid(self, form):
        form.instance.status = 'processing'
        super(EditProduct, self).form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('store-detail', args=[self.object.store.id])


class GetProductFields(LoginRequiredMixin, IsSeller, IsProductOwner, ListView):
    login_url = '/accounts/login/'
    template_name = 'product-detail.html'
    model = ProductDetail
    context_object_name = 'fields'

    def get_queryset(self):
        product_slug = self.kwargs['slug']
        return ProductDetail.objects.filter(product__slug=product_slug)


class StoreOrder(LoginRequiredMixin, IsSeller, IsStoreOwner, View):
    login_url = '/accounts/login/'
    template_name = 'store-orders.html'
    form = DateForm

    def get(self, request, pk):
        orders = Order.objects.filter(cart__cartitem__product__store=pk)
        return render(request, self.template_name, {'form': self.form, 'orders': orders})

    def post(self, request, pk):
        if request.POST.get('date'):
            start = datetime.strptime(request.POST.get('start')[:-3], '%m/%d/%Y %H:%M')
            end = datetime.strptime(request.POST.get('end')[:-3], '%m/%d/%Y %H:%M')
            orders = Order.objects.filter(cart__updated_at__range=[start, end]).filter(
                cart__cartitem__product__store=pk)
            return render(request, self.template_name, {'form': self.form, 'orders': orders})

        if request.POST.get('filter'):
            status = request.POST.get('filter')
            orders = Order.objects.filter(cart__cartitem__product__store=pk).filter(status=status)
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

        orders = Order.objects.filter(cart__cartitem__product__store=pk)
        return render(request, self.template_name, {'form': self.form, 'orders': orders})


class StoreCustomers(LoginRequiredMixin, IsSeller, IsStoreOwner, ListView):
    login_url = '/accounts/login/'
    template_name = 'store-customers.html'
    model = Order
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_orders = Order.objects.filter(cart__cartitem__product__store__id=self.kwargs['pk']).distinct()
        customers = store_orders.values(customer_id=F('cart__buyer'))
        context['info'] = []
        for customer in customers:
            id = customer['customer_id']
            name = CustomUser.objects.get(id=id).full_name()
            email = CustomUser.objects.get(id=id).email
            last_order = store_orders.filter(cart__buyer__id=id).latest('cart__updated_at').cart.updated_at
            orders = store_orders.filter(cart__buyer__id=id).aggregate(Count('cart'))['cart__count']
            products = store_orders.filter(cart__buyer__id=id).aggregate(Sum('cart__cartitem__quantity'))[
                'cart__cartitem__quantity__sum']
            total = 0
            for cart in store_orders.filter(cart__buyer__id=id).values('cart'):
                total += Cart.objects.get(id=cart['cart']).total_price()
            context['info'].append([name, email, last_order, orders, products, total])

        context['pk'] = self.kwargs['pk']
        return context


class StoreReport(LoginRequiredMixin, IsSeller, IsStoreOwner, ListView):
    login_url = '/accounts/login/'
    template_name = 'store-report.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report'] = Order.objects.filter(cart__cartitem__product__store__id=self.kwargs['pk']).values(
            'cart__cartitem__product__slug').distinct().annotate(total_amount=Sum('cart__cartitem__quantity')).annotate(
            total_price=Sum(F('cart__cartitem__quantity') * F('cart__cartitem__product__price')))
        context['pk'] = self.kwargs['pk']
        return context
