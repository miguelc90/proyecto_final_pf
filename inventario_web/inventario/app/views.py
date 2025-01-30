
import pandas as pd
from django.db.models import Sum
from decimal import Decimal
import os, locale
from django.http import Http404, HttpResponse, HttpResponseRedirect #revisar si no se usa
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.core.files import File
from datetime import datetime
from django.utils import timezone

from inventario import settings
from .models import Producto, Transacciones, UserSession, Proveedor, ProductoProveedor, CarritoItem, CarritoHistorial
from .models import Categoria
from .forms import ProductoForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from django_plotly_dash import DjangoDash #revisar si no se usa
import plotly.express as px


# Create your views here.

#permisos
def is_admin(user):
    return user.is_superuser

#inicio
@login_required
def home(request):
    #datos para las tarjetas
    pedidos_realizados = CarritoHistorial.objects.count()
    pedidos_pendientes = CarritoHistorial.objects.filter(estado='pendiente').count()
    producto_activo = Producto.objects.filter(activo=True).count()
    producto_inactivo = Producto.objects.filter(activo=False).count()
    proveedor_activo = Proveedor.objects.filter(activo=True).count()
    proveedor_inactivo = Proveedor.objects.filter(activo=False).count()
    productos_cargados = producto_activo+producto_inactivo

    #grafico
    categorias = Categoria.objects.all()
    nombres_categorias = []
    datos = []

    for categoria in categorias:
        cantidad = Producto.objects.filter(categoria=categoria).count()
        nombres_categorias.append(categoria.nombre)
        datos.append(cantidad)

    # Normalizar los datos para aplicar una escala de colores
    max_dato = max(datos) if datos else 1
    colores = sample_colorscale('Viridis', [cantidad / max_dato for cantidad in datos])

    # Crear un gráfico moderno
    fig = go.Figure(data=[
        go.Bar(
            x=nombres_categorias,
            y=datos,
            text=datos,
            textposition='auto',
            marker=dict(
                color=colores,
                line=dict(color='rgba(0, 0, 0, 0.8)', width=1.5) 
            ),
            hoverinfo='x+y',
        )
    ])

    # Personalizar el diseño
    fig.update_layout(
        title=dict(
            text="Cantidad de Productos por Categoría",
            x=0.5,
            font=dict(size=24, color='rgba(58, 71, 80, 1.0)')
        ),
        xaxis=dict(
            title="Categorías",
            titlefont=dict(size=18, color='rgba(58, 71, 80, 1.0)'),
            tickfont=dict(size=14, color='rgba(58, 71, 80, 0.8)'),
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        yaxis=dict(
            title="Cantidad de Productos",
            titlefont=dict(size=18, color='rgba(58, 71, 80, 1.0)'),
            tickfont=dict(size=14, color='rgba(58, 71, 80, 0.8)'),
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        legend=dict(
            bgcolor='rgba(230, 230, 240, 0.5)',  
            bordercolor='rgba(0, 0, 0, 0.3)',    
            borderwidth=1,
            font=dict(size=14, color='rgba(58, 71, 80, 1.0)')
        ),
        # Fondo del gráfico y área completa
        plot_bgcolor='rgba(230, 230, 240, 1)',
        paper_bgcolor='rgba(245, 245, 250, 1)',
        margin=dict(t=70, l=50, r=50, b=70),
        showlegend=False,
    )


    # Convertir el gráfico a HTML
    grafico_html = fig.to_html(full_html=False)

    data = {
        'activos':producto_activo,
        'inactivos':producto_inactivo,
        'proveedores_activos':proveedor_activo,
        'proveedores_inactivos':proveedor_inactivo,
        'productos_cargados':productos_cargados,
        'pedidos_realizados':pedidos_realizados,
        'pedidos_pendientes':pedidos_pendientes,
        'grafico':grafico_html,
    }
    return render(request, "inventario/home.html", data)

#paginados
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

#sesiones

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

@user_passes_test(is_admin, login_url='/listado/')
def sesion_usuario(request):
    sesiones = UserSession.objects.all().order_by('-login_time')

    sesiones_paginadas = paginado_proveedores(request, sesiones, 15)

    return render(request, 'inventario/sesion_usuario.html', {
        'sesiones': sesiones_paginadas,
        'paginator': sesiones_paginadas.paginator,
        'contexto': 'sesiones'
    })

#inventario

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

@login_required
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

@login_required
@user_passes_test(is_admin, login_url='/listado/')
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    messages.success(request, 'el producto se eliminó correctamente')
    return redirect(to='listado')

#proveedores
@login_required
@user_passes_test(is_admin, login_url='/listado/')
def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    data = {
        'proveedores': proveedores
    }
    return render(request, 'proveedores/proveedores.html', data)

@login_required
@user_passes_test(is_admin, login_url='/listado/')
def proveedor_bebidas(request):
    bebidas = ProductoProveedor.objects.filter(proveedor__nombre="SRB Distribuidora").order_by('nombre')
    bebidas_paginadas = paginado_proveedores(request, bebidas)
    data = {
        'bebidas':bebidas_paginadas,
        'paginator':bebidas_paginadas.paginator,
        'contexto':'bebidas'
    }
    return render(request, 'proveedores/proveedor_bebidas.html', data)

@login_required
@user_passes_test(is_admin, login_url='/listado/')
def proveedor_alimentos(request):
    articulos = ProductoProveedor.objects.filter(proveedor__nombre="Grupo Almar").order_by('nombre')
    articulos_paginados = paginado_proveedores(request, articulos)
    data = {
        'articulos':articulos_paginados,
        'paginator':articulos_paginados.paginator,
        'contexto':'articulos'
    }
    return render(request, 'proveedores/proveedor_alimentos.html', data)

@login_required
@user_passes_test(is_admin, login_url='/listado/')
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

@user_passes_test(is_admin, login_url='/listado/')
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

@user_passes_test(is_admin, login_url='/listado/')
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(ProductoProveedor, id=producto_id)

    carrito_item, created = CarritoItem.objects.get_or_create(
        producto=producto,
        procesado=False,
        eliminado=False,
        defaults={'proveedor': producto.proveedor}
    )
    
    carrito_item.sub_total = carrito_item.producto.precio_bulto * carrito_item.cantidad
    carrito_item.total_a_pagar = carrito_item.sub_total
    
    carrito_item.proveedor = producto.proveedor
    carrito_item.save() 

    messages.success(request, f"El producto {producto} se agregó al carrito correctamente")
    
    if producto.proveedor.nombre == "SRB Distribuidora":
        return redirect("bebidas")
    elif producto.proveedor.nombre == "Grupo Almar":
        return redirect("alimentos")
    elif producto.proveedor.nombre == "Congelados Food":
        return redirect("congelados")
    
    return render(request, "inventario/home.html")

@user_passes_test(is_admin, login_url='/listado/')
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

    locale.setlocale(locale.LC_TIME, 'es_AR.UTF-8')
    fecha_actual = datetime.now()
    formato_local = fecha_actual.strftime("%A, %d de %B de %Y")

    def agregar_encabezado():
        """Función para agregar encabezado y columnas."""
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Lista de Productos del Carrito")
        p.setFont("Helvetica", 12)
        p.drawString(100, 730, f"Fecha: {formato_local}")
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, 700, "Producto")
        p.drawString(200, 700, "Cantidad")
        p.drawString(300, 700, "Precio por bulto")
        p.drawString(420, 700, "Proveedor")
        p.drawString(530, 700, "Subtotal")

    agregar_encabezado()

    y = 680 
    sub_total = 0
    for item in carrito_items:
        if y < 50:
            p.showPage()
            agregar_encabezado()
            y = 680

        p.setFont("Helvetica", 12)
        p.drawString(100, y, item.producto.nombre)
        p.drawString(200, y, str(item.cantidad))
        p.drawString(300, y, f"${item.producto.precio_bulto}")
        item.sub_total = item.producto.precio_bulto * item.cantidad
        p.drawString(420, y, f"{item.proveedor}")
        p.drawString(530, y, f"${item.sub_total}")
        y -= 20
        sub_total += item.sub_total

    total_a_pagar = sub_total

    # Agregar total a pagar en la última página
    if y < 70:
        p.showPage()
        agregar_encabezado()
        y = 680

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y - 40, f"Total a pagar: ${total_a_pagar}")

    # Guardar el PDF
    p.showPage()
    p.save()
    return pdf_path

@user_passes_test(is_admin, login_url='/listado/')
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
                proveedor=item.proveedor,
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

@user_passes_test(is_admin, login_url='/listado/')
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

#Reportes
@login_required
def productos_bajo_stock(request, umbral=50):
    # Consulta de productos con baja cantidad
    productos_bajo_stock = Producto.objects.filter(cantidad_stock__lte=umbral, activo=True)

    # Crear un DataFrame con los datos necesarios
    data = {
        'Producto': [producto.nombre for producto in productos_bajo_stock],
        'Stock': [producto.cantidad_stock for producto in productos_bajo_stock]
    }
    df = pd.DataFrame(data)

    # Crear el gráfico
    fig = px.bar(
        df,
        x='Producto',
        y='Stock',
        labels={'Producto': 'Producto', 'Stock': 'Cantidad en Stock'},
        title='Productos con menos de 50 unidades'
    )

    # Pasar los productos y el gráfico a la plantilla
    return render(request, 'inventario/reportes/productos_bajo_stock.html', {
        'productos_bajo_stock': productos_bajo_stock,
        'grafico': fig.to_html(full_html=False) 
    })

#Balances
@login_required
def balance_inventario(request):
    # datos gráfico de barras (por categorías)
    productos = Producto.objects.filter(activo=True)
    data_categorias = productos.values('categoria__nombre').annotate(
        stock_total=Sum('cantidad_stock')
    )
    df_categorias = pd.DataFrame(data_categorias)

    # Gráfico de barras (categorías)
    fig_bar = px.bar(
        df_categorias,
        x='categoria__nombre',
        y='stock_total',
        labels={'categoria__nombre': 'Categoría', 'stock_total': 'Cantidad Total'},
        title='Stock Total por Categoría'
    )

    # datos gráfico de torta (proveedores)
    data_proveedores = productos.values('proveedor__nombre').annotate(
        stock_total=Sum('cantidad_stock')
    )
    df_proveedores = pd.DataFrame(data_proveedores)

    # Gráfico de torta (proveedores)
    fig_pie_proveedor = px.pie(
        df_proveedores,
        names='proveedor__nombre',
        values='stock_total',
        title='Stock Total por Proveedor'
    )

    # datos gráfico de torta (marcas)
    data_marcas = productos.values('marca__nombre').annotate(
        stock_total=Sum('cantidad_stock')
    )
    df_marcas = pd.DataFrame(data_marcas)

    # Gráfico de torta (marcas)
    fig_pie_marca = px.pie(
        df_marcas,
        names='marca__nombre',
        values='stock_total',
        title='Stock Total por Marca'
    )

    # Renderizar la página con todos los gráficos
    return render(request, 'inventario/balances/balance_inventario.html', {
        'graph_bar': fig_bar.to_html(full_html=False),
        'graph_pie_proveedor': fig_pie_proveedor.to_html(full_html=False),
        'graph_pie_marca': fig_pie_marca.to_html(full_html=False)
    })

#Estadisticas
@login_required
def producto_mas_comprado(request):
    productos_data = CarritoHistorial.objects.values('producto', 'producto__nombre', 'producto__proveedor__nombre') \
        .annotate(total_encargados=Sum('cantidad')) \
        .order_by('-total_encargados')[:10]  # Los 10 productos más encargados

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(productos_data)

    # Renombrar columnas para facilitar su uso en Plotly
    df.rename(columns={
        'producto__nombre': 'Producto',
        'producto__proveedor__nombre': 'Proveedor',
        'total_encargados': 'Cantidad Encargada'
    }, inplace=True)

    # Crear gráfico de líneas con Plotly
    fig = px.line(
        df,
        x='Producto', 
        y='Cantidad Encargada',  
        markers=True,  
        color='Proveedor', 
        labels={'Producto': 'Producto', 'Cantidad Encargada': 'Cantidad Encargada'},
        title='Productos Más Encargados a Proveedores',
        line_shape='linear',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig.update_layout(
        xaxis_title='Producto',
        yaxis_title='Cantidad Encargada',
        template='plotly_white',
        showlegend=True
    )

    # Renderizar el gráfico en la plantilla
    return render(request, 'inventario/estadisticas/producto_mas_comprado.html', {
        'grafico': fig.to_html(full_html=False)
    })

#Pedidos
@login_required
def pedidos_realizados(request):
    #obtener los datos de los pedidos actualizados
    pedidos = CarritoHistorial.objects.all()
    for pedido in pedidos:
        if pedido.fecha_de_entrega and pedido.fecha_de_entrega.date() == timezone.now().date():
            pedido.estado = 'entregado'
        else:
            pedido.estado = 'pendiente'
        pedido.save()

    pedidos = CarritoHistorial.objects.filter(procesado=True).order_by('-fecha_procesado')
    pedidos_paginados = paginado_proveedores(request, pedidos, 15)

    return render(request, 'inventario/pedidos_realizados.html',{
        'pedidos':pedidos_paginados,
        'paginator':pedidos_paginados.paginator,
        'contexto':'pedidos'
    })

#Soporte
@login_required
def soporte(request):
    return render(request, 'inventario/soporte.html')