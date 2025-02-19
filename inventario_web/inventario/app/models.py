from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import random

#funciones
def generar_codigo_aleatorio():
    return random.randint(1000000000, 2147483647)
# Create your models here.

class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre
    
class Proveedor(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50, default="proveedor")
    activo = models.BooleanField()
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
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    procesado = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad}'
    

class Transacciones(models.Model):
    total_final_a_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='transacciones_pdfs/', null=True, blank=True)

    def __str__(self):
        return f'Transacción {self.id} - Total: {self.total_final_a_pagar}'
    
class CarritoHistorial(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('entregado', 'Entregado'),
    ]

    producto = models.ForeignKey(ProductoProveedor, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    procesado = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)
    fecha_procesado = models.DateTimeField(auto_now_add=True)
    fecha_de_entrega = models.DateTimeField(blank=True, null=True)
    transaccion = models.ForeignKey(Transacciones, on_delete=models.CASCADE, related_name='items')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')

    def save(self, *args, **kwargs):
        if not self.fecha_procesado:
            self.fecha_procesado = timezone.now()

        if not self.fecha_de_entrega:
            self.fecha_de_entrega = self.fecha_procesado + timedelta(days=1)

        # Convertir fecha_de_entrega a la zona horaria local
        fecha_entrega_local = timezone.localtime(self.fecha_de_entrega)

        # Verificar si la fecha de entrega coincide con la fecha actual en la zona horaria local
        if fecha_entrega_local.date() <= timezone.localtime(timezone.now()).date():
            self.estado = 'entregado'
        else:
            self.estado = 'pendiente'

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} - {self.estado}'

    


