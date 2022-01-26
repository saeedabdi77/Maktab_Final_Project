from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from .models import Store, Product


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
