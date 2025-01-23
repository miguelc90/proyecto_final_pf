from django import forms
from .models import Producto, CarritoItem
from django.forms import ValidationError


class ProductoForm(forms.ModelForm):

    nombre = forms.CharField(min_length=3, max_length=50)

    class Meta:
        model = Producto
        fields = "__all__"
        widgets = {
            'fecha_fabricacion': forms.SelectDateWidget()
        }


class CarritoItemForm(forms.ModelForm):
    class Meta:
        model = CarritoItem
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.HiddenInput(),
            'cantidad': forms.HiddenInput(),
        }

