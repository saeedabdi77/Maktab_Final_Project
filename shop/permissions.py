from django.http import HttpResponseForbidden
from .models import Store, Product
from users.models import Seller
from django.shortcuts import reverse, redirect


class IsStoreOwner(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.seller != Store.objects.get(pk=kwargs['pk']).owner:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class IsProductOwner(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(pk=kwargs['pk'])
        except:
            product = Product.objects.get(slug=kwargs['slug'])
        if request.user.seller != product.store.owner:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class IsSeller(object):
    def dispatch(self, request, *args, **kwargs):
        if not Seller.objects.filter(user=request.user).exists():
            return redirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)
