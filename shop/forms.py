from django import forms
from .models import Store, Product, ProductImage, ProductDetail
from users.models import Address
from cities_light.models import City, Region
from multiupload.fields import MultiImageField


class AddStoreForm(forms.ModelForm):
    province = forms.ChoiceField(choices=[(item.pk, item) for item in Region.objects.all()])
    city = forms.ChoiceField(choices=[(item.pk, item) for item in City.objects.all()])
    zip_code = forms.CharField(max_length=15)
    address_description = forms.CharField(max_length=250)

    class Meta:
        model = Store
        fields = ('address_description', 'name', 'type', 'province', 'city', 'zip_code', 'image')


class AddProductForm(forms.ModelForm):
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Product
        fields = ('brand', 'name', 'type', 'description', 'price', 'quantity', 'images')


class DateForm(forms.Form):
    start = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )
    end = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )


class ProductFieldsForm(forms.Form):
    def __init__(self, keys, *args, **kwargs ):
        super(ProductFieldsForm, self).__init__(*args, **kwargs)
        for detail in keys:
            self.fields[detail.name] = forms.CharField(max_length=50)
