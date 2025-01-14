from django.contrib import admin
from .models import Marca, Proveedor, Categoria, Producto

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "descripcion", "codigo_barras", "peso_neto",
                    "fecha_de_registro", "fecha_de_vencimiento", "cantidad_stock",
                    "precio_unitario", "marca", "proveedor", "categoria", "activo"]
    
    search_fields = ["nombre"]
    list_filter = ["activo", "precio_unitario"]
    list_per_page = 5

admin.site.register(Marca)
admin.site.register(Proveedor)
admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)

