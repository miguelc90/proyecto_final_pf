from django import forms
from .models import Producto
from django.forms import ValidationError


class ProductoForm(forms.ModelForm):

    nombre = forms.CharField(min_length=3, max_length=50)

    class Meta:
        model = Producto
        fields = "__all__"
        widgets = {
            'fecha_fabricacion': forms.SelectDateWidget()
        }
