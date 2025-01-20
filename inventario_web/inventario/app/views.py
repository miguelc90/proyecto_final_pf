from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from .models import Producto, UserSession, Proveedor, ProductoProveedor
from .forms import ProductoForm
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