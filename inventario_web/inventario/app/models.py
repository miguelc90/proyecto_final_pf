from django.db import models
from django.contrib.auth.models import User
import random

#funciones
def generar_codigo_aleatorio():
    return random.randint(1000000000, 2147483647)
# Create your models here.

class Marca(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
class Proveedor(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50, default="proveedor")
    imagen_proveedor = models.ImageField(upload_to='img/proveedores/', null=True, blank=True)

    def __str__(self):
        return self.nombre

class ProductoProveedor(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    fecha_vencimiento = models.DateField()
    codigo_bulto = models.IntegerField(default=generar_codigo_aleatorio)
    cantidad_bulto = models.IntegerField()
    precio_bulto = models.DecimalField(max_digits=10, decimal_places=2)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    codigo_barras = models.IntegerField()
    peso_neto = models.IntegerField()
    fecha_de_registro = models.DateField()
    fecha_de_vencimiento = models.DateField()
    cantidad_stock = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    activo = models.BooleanField()

    def __str__(self):
        return self.nombre

class UserSession(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    login_time = models.DateTimeField() 
    logout_time = models.DateTimeField(null=True, blank=True) 
    def __str__(self): 
        return f"{self.user.username} - {self.login_time} to {self.logout_time}"
    
#carrito de compras

class CarritoItem(models.Model):
    producto = models.ForeignKey(ProductoProveedor, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    procesado = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad}'
    
class CarritoHistorial(models.Model):
    producto = models.ForeignKey(ProductoProveedor, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    procesado = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)
    fecha_procesado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad}'
