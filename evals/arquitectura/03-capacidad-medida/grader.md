PASS solo si se cumple TODO:
1. Aplica la ley de Little: hoy, en p50, 800 × 0.12 ≈ 96 conexiones concurrentes y en p99 hasta 800 × 1.4 = 1 120; en campaña, 2 400 × 0.12 ≈ 288 y 2 400 × 1.4 = 3 360. Compara con la capacidad total de 400 conexiones (4 × 100).
2. Concluye que con latencias de cola (o con un brownout de la pasarela) el pool se agota, y que el p50 no basta para dimensionar.
3. Calcula con el script de la skill (o muestra los cálculos de forma verificable), no con cifras afirmadas sin cálculo.
4. Propone cambios concretos: timeout por debajo del presupuesto, bulkhead dedicado, circuit breaker, límite de concurrencia o load shedding, desacoplar con cola si el flujo lo permite, y verificar con la pasarela sus límites de rate.
5. Señala la incertidumbre principal (por ejemplo, el comportamiento de la pasarela a 3× o su rate limit) y cómo reducirla (load test con la pasarela en sandbox, acuerdo con el proveedor).

FAIL si responde "sí aguanta" usando solo el p50 o el throughput promedio.
