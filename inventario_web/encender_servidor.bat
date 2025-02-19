@echo off

REM Activar entorno virtual
call C:\Users\HP\Documents\programacion\inventario_web\env\Scripts\activate.bat

REM Iniciar las tareas en segundo plano
start /B python C:\Users\HP\Documents\programacion\inventario_web\inventario\manage.py process_tasks

REM Iniciar el servidor de Django en segundo plano
start /B python C:\Users\HP\Documents\programacion\inventario_web\inventario\manage.py runserver

REM Esperar unos segundos para asegurarse de que el servidor se haya iniciado
timeout /t 15 /nobreak

REM Ejecutar la tarea de actualización de pedidos
python C:\Users\HP\Documents\programacion\inventario_web\inventario\manage.py shell -c "from app.tasks import actualizar_estados_pedidos; actualizar_estados_pedidos()"
