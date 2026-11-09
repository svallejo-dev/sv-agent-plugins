# Contratos: Pact entre servicios propios, learning tests para terceros

Pact es testing de contratos **dirigido por el consumidor**:
1. El consumidor escribe un test contra un mock de Pact declarando qué pide y qué espera; Pact genera un **archivo de contrato** JSON.
2. El proveedor reproduce ese contrato contra su implementación real, preparando cada estado con *state handlers*; si cambió algo que el consumidor usa, falla.

**Analogía:** un contrato de arriendo. Firmado y guardado en un cajón (modo A) sigue valiendo, pero solo si alguien lo lee cuando hay una disputa. Registrado en notaría (modo D, con broker), cualquiera puede consultarlo antes de actuar.

## Quién hace qué

- Los **tests de consumidor** usan el cliente real del consumidor, que es código de producción. Por eso son del **dev** y viven con el código del consumidor, **no** en la carpeta de aceptación (que es caja negra y está sellada).
- Los **archivos de contrato** generados van a `contracts/` del repo, fuera de lo sellado.
- La **verificación del proveedor** es el peldaño 2: la ejecuta su script, y el resultado (fecha, versión del proveedor) queda en los reportes de esa ejecución, no dentro del contrato.

## Modos para servicios que controlas

No hace falta CI ni broker para que funcione: el contrato es un archivo y la verificación es un comando. Lo que cambia entre modos es **qué garantía obtienes y quién tiene que acordarse de ejecutarlo**.

| Modo | Cómo | Cuándo | Qué pierdes |
|---|---|---|---|
| **A. Local con archivos** | El test del consumidor escribe `contracts/*.json`; el proveedor se verifica levantado en el peldaño 1, con state handlers que siembran por sus seams | Controlas ambos lados o puedes levantar el proveedor | `can-i-deploy` y el historial de versiones; el drift solo se detecta cuando alguien ejecuta la verificación |
| **B. Contra ambiente desplegado** | La verificación apunta a la URL del proveedor en dev o staging | No puedes levantar el proveedor | Sin control de estado: solo interacciones sin estado o con datos sembrados conocidos; más inestable |
| **D. CI con broker** | Contratos publicados en un Pact Broker; `can-i-deploy` antes de desplegar | Hay permisos y ambos equipos lo adoptan | — |

### Sin CI: cómo no dejarlo morir

Sin CI, Pact pasa de ser una **puerta** a ser una **verificación que alguien tiene que acordarse de ejecutar**. Para que no se pudra en silencio:
1. La verificación forma parte del script del peldaño 2.
2. `qa-verify` lo ejecuta en el **ritmo completo** y lo reporta como puerta.
3. `qa-verify` marca como riesgo un contrato cuya última verificación verde tenga más de 30 días o sea anterior al último cambio del proveedor.

## Terceros: no uses Pact como si fuera una puerta

Con un tercero (pasarela de pagos, partner), la verificación del proveedor no es viable: no ejecutará tu contrato y su sandbox no expone *provider states*. La propia documentación de Pact desaconseja usarlo para APIs que no controlas. En su lugar:

1. **Learning tests** contra el sandbox (peldaño 2): cada suposición sobre el tercero es un test que se ejecuta en el ritmo completo y avisa si el tercero cambia.
2. **WireMock** graba esas respuestas como fakes para el peldaño 1.
3. Si el tercero publica un **OpenAPI**, el contract testing bidireccional (comparar lo que consumes contra su OpenAPI; lo ofrece PactFlow, de pago) es una opción adicional, no un sustituto de los learning tests.

## Recetas (Pact Go v2)

Las firmas cambian entre versiones; confírmalas en la documentación de la versión instalada. Pact Go v2 necesita la librería nativa de Pact.

Consumidor (lo escribe el dev, junto al código del consumidor):

```go
mock, err := consumer.NewV4Pact(consumer.MockHTTPProviderConfig{
    Consumer: "front-checkout", Provider: "bff-pagos", PactDir: "../contracts",
})
if err != nil { t.Fatal(err) }
err = mock.AddInteraction().
    Given("existe un comprador nuevo").
    UponReceiving("una solicitud de token para checkout").
    WithRequest("POST", "/tokens", func(b *consumer.V4RequestBuilder) {
        b.JSONBody(map[string]any{"flujo": "checkout"})
    }).
    WillRespondWith(200, func(b *consumer.V4ResponseBuilder) {
        b.JSONBody(matchers.Map{
            "tipo":  matchers.S("client_token"),
            "token": matchers.Regex("eyJhbGciOi.e30.x", `^[\w-]+\.[\w-]+\.[\w-]*$`),
        })
    }).
    ExecuteTest(t, func(cfg consumer.MockServerConfig) error {
        return clienteCheckout(fmt.Sprintf("http://%s:%d", cfg.Host, cfg.Port)).PedirToken("checkout")
    })
```

Proveedor (peldaño 2):

```go
err := provider.NewVerifier().VerifyProvider(t, provider.VerifyRequest{
    ProviderBaseURL: os.Getenv("BASE_URL"),
    PactFiles:       []string{"../contracts/front-checkout-bff-pagos.json"},
    StateHandlers: models.StateHandlers{
        "existe un comprador nuevo": func(setup bool, s models.ProviderState) (models.ProviderStateResponse, error) {
            return nil, sembrarCompradorNuevo(setup) // por el seam de siembra, no tocando la base
        },
    },
})
```

**El detalle que importa:** el contrato debe nacer de lo que el **consumidor real necesita** (la documentación del SDK, el código del front), no de lo que el proveedor devuelve hoy. Un contrato copiado de la respuesta actual del proveedor certifica el bug.
