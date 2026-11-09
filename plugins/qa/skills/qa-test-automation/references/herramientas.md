# Herramientas: cómo se usa cada una

Recetas mínimas para el harness y los tests. Las APIs cambian entre versiones: **confirma cada firma y cada flag con la documentación o el `--help` de la versión instalada** antes de dar por buena una receta. El criterio de selección está en `qa-toolbox`.

## Hurl: flujos HTTP en texto plano

Binario independiente del lenguaje. Cada archivo es una secuencia de peticiones con capturas y aserciones; lo lee un humano sin saber programar.

```hurl
# ESC-07-idempotencia.hurl
# Siembra por la API: un cliente nuevo y único por ejecución
POST {{base_url}}/qa/clientes
HTTP 201
[Captures]
cliente: jsonpath "$.id"

POST {{base_url}}/clientes/{{cliente}}/dispositivos
Idempotency-Key: alta-{{cliente}}
{ "tipo": "tv" }
HTTP 201
[Captures]
id: jsonpath "$.id"

POST {{base_url}}/clientes/{{cliente}}/dispositivos
Idempotency-Key: alta-{{cliente}}
{ "tipo": "tv" }
HTTP 201
[Asserts]
jsonpath "$.id" == {{id}}

GET {{base_url}}/clientes/{{cliente}}/dispositivos
HTTP 200
[Asserts]
jsonpath "$.items" count == 1
```

- Ejecución (dentro del script de peldaño): `hurl --test --report-junit "$QA_REPORTES/hurl.xml" --variable base_url=$BASE_URL <archivos>`.
- Sondeo sin `sleep`: la opción `retry` por petición (sección `[Options]`).
- Morfología: `jsonpath "$.token" matches "^[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]*$"`.
- El ID va en el nombre del archivo.

## Gherkin con godog (Go)

Gherkin es el artefacto que lee el humano; godog conecta cada paso con una función Go. Admite español con `# language: es`.

```gherkin
# language: es
Característica: Límite de dispositivos por cliente
  Esquema del escenario: ESC-04 registrar con <actuales> dispositivos
    Dado un cliente con <actuales> dispositivos registrados
    Cuando registra un nuevo dispositivo
    Entonces la respuesta es <estado>
    Y el cliente queda con <final> dispositivos
    Ejemplos:
      | actuales | estado | final |
      | 4        | 201    | 5     |
      | 5        | 409    | 5     |
```

```go
func InitializeScenario(sc *godog.ScenarioContext) {
    w := &mundo{api: nuevoClienteHTTP(os.Getenv("BASE_URL"))} // estado por escenario
    sc.Step(`^un cliente con (\d+) dispositivos registrados$`, w.clienteConDispositivos)
    sc.Step(`^registra un nuevo dispositivo$`, w.registraDispositivo)
    sc.Step(`^la respuesta es (\d+)$`, w.respuestaEs)
    sc.Step(`^el cliente queda con (\d+) dispositivos$`, w.clienteQuedaCon)
}
```

- Los pasos hablan HTTP con el servicio; nunca importan paquetes de producción.
- Se ejecuta desde `go test` con `godog.TestSuite`; el JUnit sale de su formateador `junit` (por ejemplo `Format: "pretty,junit:" + os.Getenv("QA_REPORTES") + "/godog.xml"`; confirma la sintaxis en tu versión). Los pasos viven en el módulo Go propio de la carpeta de aceptación.
- En otros lenguajes, el equivalente es Cucumber (JVM, JS) o behave (Python). Karate es una alternativa con su propio DSL HTTP.

## Testcontainers: dependencias reales y desechables

Levanta contenedores desde el test y los destruye al terminar. Existe para Go, Java, .NET, Node, Python y otros.

```go
pg, err := postgres.Run(ctx, "postgres:16-alpine",
    postgres.WithDatabase("dispositivos"),
    postgres.BasicWaitStrategies())
if err != nil { t.Fatal(err) }
t.Cleanup(func() { _ = testcontainers.TerminateContainer(pg) })
dsn, err := pg.ConnectionString(ctx, "sslmode=disable")
if err != nil { t.Fatal(err) }
```

Para el peldaño 1, el **servicio bajo prueba también es un contenedor**, construido desde su imagen, en la misma red de Docker que sus dependencias. Así el QA prueba el artefacto que se despliega, no el código fuente.

Requisitos: Docker disponible en local y en CI. Fija las versiones de las imágenes; `latest` hace el harness no determinista.

## Toxiproxy: fallos de red a voluntad

Proxy TCP que se intercala entre el servicio y cada dependencia. El servicio se configura para hablar con el proxy; el test añade "toxics".

```go
cli := toxiproxy.NewClient(toxiproxyAPI) // la API del contenedor de Toxiproxy (puerto 8474 mapeado)
px, err := cli.CreateProxy("postgres", "0.0.0.0:25432", "postgres:5432")
if err != nil { t.Fatal(err) }
// el servicio bajo prueba se configura con la base en <toxiproxy>:25432
if _, err := px.AddToxic("lenta", "latency", "downstream", 1.0,
    toxiproxy.Attributes{"latency": 3000}); err != nil { t.Fatal(err) }
t.Cleanup(func() { _ = px.RemoveToxic("lenta") })
```

Toxics útiles: `latency`, `bandwidth`, `timeout`, `reset_peer`, `slicer`, `limit_data`, `slow_close`. Deshabilitar el proxy simula la dependencia caída.

Se usa en el peldaño 1, donde controlas toda la red. **No en staging compartido.**

## WireMock: fakes de terceros grabados de la realidad

Servidor HTTP de stubs, como contenedor (tiene módulo para Testcontainers). Dos usos:
- **Grabación**: en modo record actúa de proxy hacia el sandbox del tercero mientras corren los learning tests y guarda las respuestas como mappings. **Redacta tokens y secretos de los mappings antes de guardarlos.**
- **Reproducción**: en el peldaño 1 sirve esos mappings, más los de errores y variantes que el sandbox no deja provocar (5xx, 429, timeouts con `fixedDelayMilliseconds`, respuestas truncadas).

## Pact: contratos entre servicios propios

Ver [pact-modos.md](pact-modos.md): modos A (archivos locales), B (contra ambiente desplegado) y D (CI con broker). Para terceros, learning tests + WireMock.

## Schemathesis: fuzzing de contrato desde OpenAPI

Genera miles de peticiones a partir del OpenAPI y verifica que el servicio no responda 5xx, que las respuestas cumplan el esquema y otras propiedades. Se ejecuta en el ritmo completo contra el peldaño 1. Básico: `schemathesis run <openapi> --url $BASE_URL`, con su reporte JUnit. La CLI cambió en la v4: confirma los flags con `schemathesis run --help`.

Encuentra lo que nadie escribió (entradas raras, campos extra); no reemplaza a los escenarios, que verifican reglas de negocio.

## Playwright: el consumidor real en el navegador

Para escenarios con UI y, sobre todo, para el **walking skeleton** con un SDK de navegador: una página mínima que pide el token al sistema bajo prueba, inicializa el SDK con él y expone el resultado que reporta **el propio SDK** (su callback de error o de listo).

```ts
test('ESC-01 el SDK de pagos se inicializa con el token del BFF', async ({ page }) => {
  await page.goto(`${process.env.QA_PAGINAS_URL}/checkout-minimo.html?bff=${encodeURIComponent(process.env.BASE_URL!)}`);
  await expect(page.getByTestId('sdk-estado')).toHaveText('listo', { timeout: 15000 });
});
```

**La página mínima la escribe el QA** dentro de `<Aceptación>/<feature>/` y la sirve el harness (un servidor estático en su propio contenedor). Si la sirviera el servicio bajo prueba, el dev controlaría el oráculo: podría hacer que dijera `listo` siempre.

Reportes: configura el reporter `junit` con su archivo de salida en `$QA_REPORTES` (opción `outputFile` en la config, o la variable de entorno que documente tu versión; sin ella escribe a stdout) y `outputDir` también bajo `$QA_REPORTES`: por defecto Playwright escribe `test-results/` junto a los tests, y eso rompería el sello.

Los agentes de Playwright (planner, generator, healer) pueden ayudar a crear y mantener tests de UI, pero **el healer solo puede tocar selectores, nunca aserciones**: si repara una aserción, está cambiando el oráculo.

## k6: carga

No forma parte de la suite funcional. Se usa para pruebas de carga dedicadas, en un ambiente que se pueda cargar sin afectar a otros equipos.

## gotestsum (Go)

Si parte del harness corre con `go test`, `gotestsum --junitfile "$QA_REPORTES/go.xml"` produce el JUnit. Los subtests aparecen como `TestX/ESC-11_timeout…`; `trazabilidad.py` reconoce el ID.
