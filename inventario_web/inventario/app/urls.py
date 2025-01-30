from django.urls import path
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('listado/', views.listado, name='listado'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='salir'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('buscar/', views.buscar_producto, name='buscar_producto'),
    path('modificar/<int:id>/', views.modificar_producto, name='modificar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('sesion-usuario/', views.sesion_usuario, name='sesion_usuario'),
    path('proveedores/', views.lista_proveedores, name='proveedores'),
    path('proveedor-bebidas/', views.proveedor_bebidas, name='bebidas'),
    path('proveedor-alimentos/', views.proveedor_alimentos, name='alimentos'),
    path('proveedor-congelados/', views.proveedor_congelados, name='congelados'),
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver-carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar-item/<int:id>/', views.eliminar_item, name='eliminar_item'),
    path('generar-pdf/', views.generar_pdf, name='generar_pdf'),
    path('descargar-pdf/', views.descargar_pdf, name='descargar_pdf'),
    path('pagar-productos/', views.pagar_productos, name='pagar_productos'),
    path('productos-bajo-stock/', views.productos_bajo_stock, name='productos_bajo_stock'),
    path('balances/', views.balance_inventario, name='balances'),
    path('producto-mas-comprado/', views.producto_mas_comprado, name='producto_mas_comprado'),
    path('pedidos-realizados/', views.pedidos_realizados, name='pedidos_realizados'),
    path('soporte/', views.soporte, name='soporte'),
]