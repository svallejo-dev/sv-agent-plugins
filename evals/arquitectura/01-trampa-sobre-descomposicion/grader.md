PASS solo si se cumple TODO:
1. Recomienda empezar con un monolito modular (o muy pocos servicios) sobre una base relacional, y discute explícitamente la propuesta de microservicios + Kafka.
2. Lo fundamenta con números: 2 000 órdenes/día ≈ 0.02 escrituras/s de media; una base y un desplegable lo absorben con holgura, y 6 ingenieros no pueden operar muchos servicios. Los números deben estar calculados, no solo afirmados.
3. Nombra los costes concretos de separar antes de tiempo (sagas u outbox entre órdenes e inventario, fallos de red, observabilidad y despliegues, consistencia eventual del inventario).
4. Da un camino de evolución con disparadores medibles para extraer un servicio después (crecimiento del equipo, necesidad de escalar una parte por separado, contención en despliegues).
5. Presenta una tabla de decisiones con la columna "cámbiala cuando…" con disparadores concretos.

FAIL si propone la arquitectura de cuatro servicios con Kafka como recomendación principal, o si da la razón al CTO sin cuantificar la carga.
