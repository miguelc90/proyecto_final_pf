# app/tasks.py

from background_task import background
from django.utils import timezone
from app.models import CarritoHistorial

@background(schedule=60)  # Esto ejecuta la tarea cada 60 segundos. Puedes ajustarlo a tus necesidades
def actualizar_estados_pedidos():
    print("tarea ejecutada")
    ahora_local = timezone.localtime(timezone.now())
    pedidos = CarritoHistorial.objects.filter(estado='pendiente')

    for pedido in pedidos:
        if pedido.fecha_de_entrega:
            fecha_entrega_local = timezone.localtime(pedido.fecha_de_entrega)
            if fecha_entrega_local.date() <= ahora_local.date():
                pedido.estado = 'entregado'
                pedido.save()
                print(f"Pedido {pedido.id} actualizado a entregado.")
