# Estructura del harness y reglas de datos

## Carpeta de una feature

```
<Aceptación>/
├── go.mod                módulo propio (Go): el compilador impide importar internal/ de producción
├── bin/                  scripts de peldaño (contrato en qa-setup), sellados en cada feature
└── <feature>/
    ├── .qa-sello.json    sello de integridad (no editar a mano)
    ├── README.md         qué seams usa; cómo se ejecuta
    ├── features/         Gherkin: lo que lee el humano
    ├── http/             Hurl: ESC-NN-<slug>.hurl
    ├── steps/            plomería de los pasos (generada por IA)
    ├── harness/          arranque del peldaño 1: imagen, Testcontainers, Toxiproxy, WireMock
    ├── paginas/          consumidores mínimos del walking skeleton (los escribe el QA)
    ├── aprendizaje/      learning tests contra el sandbox de terceros
    ├── fakes/            mappings de WireMock grabados y redactados + GRABACION.md con fechas
    └── datos/            generadores de datos de prueba (nunca datos reales)
```

Los escenarios de smoke del peldaño 4 son los mismos archivos, con `1, 4` en su columna Peldaño; no hay carpeta aparte con IDs duplicados. Los contratos Pact viven en `contracts/` del repo, fuera de esta carpeta (ver pact-modos.md).

Todo lo de `<feature>/` y `bin/` queda sellado, sin excepciones: el sello no ignora `node_modules`, `__pycache__` ni nada parecido, y rompe con cualquier enlace simbólico. **Nada se escribe dentro en tiempo de ejecución**: reportes, logs, cachés, `test-results/` de Playwright, `__pycache__` (usa `PYTHONDONTWRITEBYTECODE=1`) y grabaciones nuevas van a `$QA_REPORTES` o a un temporal. Si una ejecución modifica la carpeta, el sello se rompe y la verificación no puede distinguir una ejecución de una trampa.

## Datos de prueba

| Regla | Por qué |
|---|---|
| Cada escenario crea sus propios datos por la API o el seam de siembra | Sin dependencias ocultas entre escenarios ni del orden |
| Valores aleatorios por ejecución, **sin prefijos ni patrones reconocibles** | Se puede correr en paralelo y repetir sin limpiar, y el código de producción no puede reconocer los datos del test para responder lo que espera (special-casing) |
| Nunca se siembra escribiendo directo en la base del servicio | Se saltaría las reglas del sistema y el escenario probaría un estado imposible |
| En staging, solo cuentas o tenants de prueba, y limpieza al final | No ensuciar un ambiente compartido; no tocar datos de otros |
| Nunca datos personales reales; datos de tarjeta solo de prueba del proveedor | Cumplimiento (PCI, privacidad) |

Si el sistema no ofrece un seam de siembra, el escenario está `bloqueado-testabilidad`. No se "arregla" sembrando directo en la base.

## Caja negra verificable

La regla "ningún import de producción" se comprueba, no se confía:

- Go: la carpeta de aceptación es un **módulo propio**, así que importar `internal/` de producción ni siquiera compila. Además, la comprobación de `docs/agentes/qa.md` (`go list -deps -test ./...` dentro del módulo de aceptación, sin rastro del módulo de producción). `-test` es imprescindible: las suites de godog viven en archivos `_test.go`.
- Otros lenguajes: el equivalente con el analizador de dependencias, o un `grep` de las rutas de import de producción.
- Una comprobación que **falla al ejecutarse** (por ejemplo `go list` con error y salida vacía) no cuenta como superada: verifica su código de salida.

`qa-verify` ejecuta esta comprobación como puerta.

## El servicio como artefacto

En el peldaño 1, el servicio se construye una vez como imagen (`docker build`) y el harness la arranca. Probar la imagen y no el código:
- prueba lo que se despliega (configuración por variables, binario, dependencias del sistema);
- mantiene la barrera de información: el QA necesita la imagen y el handoff, no el repositorio de código.
