from decimal import Decimal
import os
from django.http import Http404, HttpResponse, HttpResponseRedirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.core.files import File

from inventario import settings
from .models import Producto, Transacciones, UserSession, Proveedor, ProductoProveedor, CarritoItem, CarritoHistorial
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
    carrito_items = CarritoItem.objects.filter(procesado=False, eliminado=False)

    total = Decimal(0)

    if request.method == 'POST':
        for item in carrito_items:
            cantidad_str = request.POST.get(f'cantidad_{item.producto.id}')
            if cantidad_str:
                try:
                    cantidad = int(cantidad_str)
                    if cantidad > 0: 
                        item.cantidad = cantidad
                        item.sub_total = item.producto.precio_bulto * cantidad
                        item.save()
                        total += item.sub_total
                except ValueError:
                    pass 

        request.session['total'] = float(total)

        return redirect('ver_carrito')

    for item in carrito_items:
        total += item.sub_total

    request.session['total'] = float(total)

    return render(request, 'inventario/ver_carrito.html', {'carrito_items': carrito_items, 'total': total})


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(ProductoProveedor, id=producto_id)
    
    cantidad = int(request.POST.get('cantidad', 1)) 

    carrito_item, created = CarritoItem.objects.get_or_create(producto=producto, procesado=False, eliminado=False)
    
    if created:
        carrito_item.cantidad = cantidad
    else:

        carrito_item.cantidad += cantidad
    
    carrito_item.sub_total = carrito_item.producto.precio_bulto * carrito_item.cantidad
    carrito_item.total_a_pagar = carrito_item.sub_total 
    carrito_item.save() 

    return redirect('bebidas')



def eliminar_item(request, id):
    producto = get_object_or_404(CarritoItem, id=id)
    producto.eliminado = True
    producto.procesado = True
    producto.delete()
    messages.success(request, 'el producto se eliminó de la lista')
    return redirect(to='ver_carrito')


def generar_pdf(carrito_items):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'transacciones_pdfs', 'carrito.pdf')
    p = canvas.Canvas(pdf_path, pagesize=letter)
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

    y = 680
    sub_total = 0
    for item in carrito_items:
        p.setFont("Helvetica", 12)
        p.drawString(100, y, item.producto.nombre)
        p.drawString(250, y, str(item.cantidad))
        p.drawString(350, y, f"${item.producto.precio_bulto}")
        item.sub_total = item.producto.precio_bulto * item.cantidad
        p.drawString(500, y, f"${item.sub_total}")
        y -= 20
        sub_total += item.sub_total 

    total_a_pagar = sub_total

    # Total a pagar
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y - 40, f"Total a pagar: ${total_a_pagar}")

    # Guardar el PDF
    p.showPage()
    p.save()
    return pdf_path

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
        
        transaccion = Transacciones.objects.create(total_final_a_pagar=total)
        pdf_path = generar_pdf(carrito_items)

        with open(pdf_path, 'rb') as pdf_file:
            transaccion.pdf.save('carrito.pdf', File(pdf_file))
        
        for item in carrito_items:
            CarritoHistorial.objects.create(
                producto=item.producto,
                cantidad=item.cantidad,
                sub_total=item.sub_total,
                total_a_pagar=item.total_a_pagar,
                procesado=True,
                eliminado=item.eliminado,
                transaccion=transaccion
            )
            item.delete()

        request.session['total'] = float(total)
        return redirect(f'/pagar-productos/?file={transaccion.id}')

    file_id = request.GET.get('file')
    return render(request, 'inventario/pagar_productos.html', {'carrito_items': carrito_items, 'total': total, 'file_id': file_id})


def descargar_pdf(request):
    file_id = request.GET.get('file')
    if not file_id:
        return HttpResponse('ID de transacción no proporcionado', status=400)

    try:
        transaccion = Transacciones.objects.get(id=file_id)
        if not transaccion.pdf:
            return HttpResponse('PDF no asociado a la transacción', status=404)

        file_path = transaccion.pdf.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        else:
            return HttpResponse('Archivo no encontrado', status=404)
    
    except Transacciones.DoesNotExist:
        return HttpResponse('Transacción no encontrada', status=404)





