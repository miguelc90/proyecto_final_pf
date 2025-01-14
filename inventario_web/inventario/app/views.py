from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import Producto
from .forms import ProductoForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.
@login_required
def home(request):
    return render(request, "inventario/home.html")

@login_required
def listado(request):
    productos = Producto.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(productos, 8)
        productos = paginator.page(page)
    except:
        raise Http404

    data = {
        'productos': productos,
        'paginator': paginator
    }
    return render(request, "inventario/listado.html", data)

def login(request):
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def buscar_producto(request): 
    query = request.GET.get('q')
    print(query) 
    if query: 
        productos = Producto.objects.filter(nombre__icontains=query) 
    else: 
        productos = Producto.objects.all()

    return render(request, 'inventario/listado.html', {'productos': productos})

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