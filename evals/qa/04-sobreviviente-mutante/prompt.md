# Caso 04: un mutante que sobrevive

## Preparación del repo de prueba

El BFF de tokens del caso 01, ya corregido: pide la variante correcta por flujo y cachea con clave `(flujo, comprador)`. La suite de aceptación tiene escenarios del SDK por flujo y de expiración, pero **ninguno** pide tokens para dos compradores distintos.

`docs/agentes/qa.md` con el comando de suite para mutantes (peldaño 1) y timeout.

## Instrucción al agente

"Prueba si nuestra suite de aceptación tiene dientes antes del PR."
