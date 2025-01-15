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
]