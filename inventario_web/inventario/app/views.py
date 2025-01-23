from decimal import Decimal
from django.http import Http404, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from .models import Producto, UserSession, Proveedor, ProductoProveedor, CarritoItem
from .forms import ProductoForm, CarritoItemForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.
@login_required
def home(request):
    return render(request, "inventario/home.html")

def paginado_inventario(request, items, items_por_pagina=7):
    page = request.GET.get('page', 1) 
    paginator = Paginator(items, items_por_pagina) 
    try: 
        items = paginator.page(page) 
    except PageNotAnInteger: 
        items = paginator.page(1) 
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def paginado_proveedores(request, queryset, items_por_pagina=10):
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, items_por_pagina)

    try:
        pagina = paginator.page(page)
    except PageNotAnInteger:
        pagina = paginator.page(1)
    except EmptyPage:
        pagina = paginator.page(paginator.num_pages)
    return pagina


@login_required
def listado(request): 
    productos = Producto.objects.all().order_by('nombre') 
    productos_paginados = paginado_inventario(request, productos) 

    data = { 
        'productos': productos_paginados, 
        'paginator': productos_paginados.paginator
    } 
    return render(request, "inventario/listado.html", data)

def login(request):
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def sesion_usuario(request):
    sesion = UserSession.objects.all()
    return render(request, 'inventario/sesion_usuario.html', {'sesiones': sesion})

def buscar_producto(request): 
    query = request.GET.get('q') 
    if query: 
        productos = Producto.objects.filter(nombre__icontains=query) 
    else: productos = Producto.objects.all().order_by('nombre')

    productos_paginados = paginado_inventario(request, productos)
 
    data = { 
        'productos': productos_paginados, 
        'paginator': productos_paginados.paginator, 
        'query': query, 
    } 
    return render(request, "inventario/listado.html", data)

@permission_required('app.add_producto')
def agregar_producto(request):
    data = {
        'form': ProductoForm()
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'producto cargado correctamente')
        else:
            data['form'] = formulario
    return render(request, 'inventario/agregar.html', data)

def modificar_producto(request, id):

    producto = get_object_or_404(Producto, id=id)

    data = {
        'form': ProductoForm(instance=producto)
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'producto modificado correctamente')
            return redirect(to='listado')
        data['form'] = formulario

    return render(request, 'inventario/modificar.html', data)

def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    messages.success(request, 'el producto se eliminó correctamente')
    return redirect(to='listado')

#proveedores

def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    data = {
        'proveedores': proveedores
    }
    return render(request, 'proveedores/proveedores.html', data)

def proveedor_bebidas(request):
    bebidas = ProductoProveedor.objects.filter(proveedor__nombre="SRB Distribuidora").order_by('nombre')
    bebidas_paginadas = paginado_proveedores(request, bebidas)
    data = {
        'bebidas':bebidas_paginadas,
        'paginator':bebidas_paginadas.paginator,
        'contexto':'bebidas'
    }
    return render(request, 'proveedores/proveedor_bebidas.html', data)

def proveedor_alimentos(request):
    articulos = ProductoProveedor.objects.filter(proveedor__nombre="Grupo Almar").order_by('nombre')
    articulos_paginados = paginado_proveedores(request, articulos)
    data = {
        'articulos':articulos_paginados,
        'paginator':articulos_paginados.paginator,
        'contexto':'articulos'
    }
    return render(request, 'proveedores/proveedor_alimentos.html', data)

def proveedor_congelados(request):
    congelados = ProductoProveedor.objects.filter(proveedor__nombre="Congelados Food").order_by('nombre')
    congelados_paginados = paginado_proveedores(request, congelados)
    data = {
        'congelados':congelados_paginados,
        'paginator':congelados_paginados.paginator,
        'contexto':'congelados'
    }
    return render(request, 'proveedores/proveedor_congelados.html', data)

#Carrito

def ver_carrito(request):
    # Obtener los items del carrito que aún no han sido procesados
    carrito_items = CarritoItem.objects.filter(procesado=False, eliminado=False)

    # Inicializar el total general
    total = Decimal(0)

    if request.method == 'POST':
        # Procesar cambios en las cantidades enviadas desde el formulario
        for item in carrito_items:
            cantidad_str = request.POST.get(f'cantidad_{item.producto.id}')  # Capturar la cantidad para cada producto
            if cantidad_str:
                try:
                    cantidad = int(cantidad_str)  # Convertir la cantidad a entero
                    if cantidad > 0:  # Solo se permiten cantidades positivas
                        # Actualizar la cantidad y recalcular el subtotal
                        item.cantidad = cantidad
                        item.sub_total = item.producto.precio_bulto * cantidad
                        item.save()  # Guardar cambios en la base de datos
                        total += item.sub_total
                except ValueError:
                    pass  # Si la cantidad no es válida, ignorar este item

        # Guardar el total en la sesión
        request.session['total'] = float(total)

        # Redirigir para actualizar la página
        return redirect('ver_carrito')

    # Si el método es GET, calcular el total general con los datos actuales del carrito
    for item in carrito_items:
        total += item.sub_total

    # Guardar el total en la sesión
    request.session['total'] = float(total)

    # Renderizar la plantilla con los datos del carrito
    return render(request, 'inventario/ver_carrito.html', {'carrito_items': carrito_items, 'total': total})


def agregar_al_carrito(request, producto_id):
    # Obtener el producto por su ID
    producto = get_object_or_404(ProductoProveedor, id=producto_id)

    if request.method == 'POST':
        # Agregar el producto al carrito con una cantidad inicial de 1
        carrito_item, created = CarritoItem.objects.get_or_create(
            producto=producto,
            procesado=False,
            eliminado=False,
            defaults={'cantidad': 1}
        )

        if not created:
            # Si el producto ya está en el carrito, no se hace nada
            pass

        # Redirigir a la lista de bebidas
        return redirect('bebidas')



def eliminar_item(request, id):
    producto = get_object_or_404(CarritoItem, id=id)
    producto.eliminado = True
    producto.save()
    messages.success(request, 'el producto se eliminó de la lista')
    return redirect(to='ver_carrito')

def generar_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carrito.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Título del PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Lista de Productos del Carrito")

    # Subtítulo con la fecha
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, "Fecha: 22 de enero de 2025")

    # Encabezados de las columnas
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 700, "Producto")
    p.drawString(250, 700, "Cantidad")
    p.drawString(350, 700, "Precio por bulto")
    p.drawString(500, 700, "Subtotal")

    # Obtén los items del carrito
    items = CarritoItem.objects.all()  # Puedes filtrar según 'procesado=False' si necesitas solo los items no procesados.

    y = 680 #REPARAR EL PDF Y LA BASE DE DATOS PARA QUE ME MUESTRE DE A UNA TRANSACCION
    sub_total = 0
    for item in items:
        # Información del producto
        p.setFont("Helvetica", 12)
        p.drawString(100, y, item.producto.nombre)
        p.drawString(250, y, str(item.cantidad))
        p.drawString(350, y, f"${item.producto.precio_bulto}")
        item.sub_total = item.producto.precio_bulto * item.cantidad
        p.drawString(500, y, f"${item.sub_total}")
        y -= 20  # Movemos la posición para el siguiente producto
        sub_total += item.sub_total  # Acumulamos el subtotal total

    # Calculamos el total a pagar (total de todos los productos)
    total_a_pagar = sub_total

    # Total a pagar
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y - 40, f"Total a pagar: ${total_a_pagar}")

    # Guardar el PDF y enviarlo como respuesta
    p.showPage()
    p.save()
    return response


def pagar_productos(request):
    total = Decimal(0)

    carrito_items = CarritoItem.objects.filter(procesado=False, eliminado=False)
    
    if request.method == 'POST':
        for item in carrito_items:
            cantidad_str = request.POST.get(f'cantidad_{item.producto.id}')
            if cantidad_str:
                try:
                    cantidad = int(cantidad_str)
                    if cantidad > 0:
                        item.cantidad = cantidad
                        item.sub_total = item.producto.precio_bulto * cantidad
                        item.total_a_pagar = item.sub_total  
                        item.save()  
                        total += item.sub_total
                    else:
                        item.delete()
                except ValueError:
                    continue
        
        request.session['total'] = float(total)

        return redirect('pagar_productos')  

    return render(request, 'inventario/pagar_productos.html', {'carrito_items': carrito_items, 'total': total})






