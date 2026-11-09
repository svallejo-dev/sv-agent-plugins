# Formato de registro de aprendizaje

Los registros de aprendizaje viven en `./registros/` con numeración secuencial: `0001-slug.md`, `0002-slug.md`, etc. Crea la carpeta de forma perezosa: solo cuando se escriba el primer registro.

Son el equivalente de los ADRs para la enseñanza: capturan lecciones no obvias, ideas clave y conocimiento previo declarado que guiarán las sesiones futuras. Sirven para calcular la zona de desarrollo próximo.

## Plantilla

```md
# {Título corto de lo aprendido o establecido}

{1-3 frases: qué se aprendió (o qué conocimiento previo quedó establecido) y por qué importa para las sesiones futuras.}
```

Ese es todo el formato. Un registro puede ser un solo párrafo. El valor está en dejar constancia de _que_ esto ya se sabe y _por qué_ cambia lo que se enseña después.

## Secciones opcionales

Inclúyelas solo cuando aporten valor real.

- **Estado** en frontmatter (`activo | reemplazado por LR-NNNN`): útil cuando una comprensión anterior resulta errónea y se reemplaza.
- **Evidencia**: cómo demostró el usuario la comprensión (una pregunta respondida, un ejercicio completado, experiencia previa citada).
- **Implicaciones**: qué desbloquea o descarta para sesiones futuras, cuando no es obvio.

## Numeración

Busca el número más alto en `./registros/` y súmale uno.

## Cuándo escribir un registro

Escribe uno cuando se cumpla alguna de estas condiciones:

1. **El usuario demostró comprensión real de algo no trivial**: no solo exposición, sino evidencia de que puede usar el concepto correctamente. Fija un nuevo suelo para lo que se enseña después.
2. **El usuario declaró conocimiento previo**: "ya sé X". Regístralo para no volver a enseñarlo, junto con la _profundidad_ declarada.
3. **Se corrigió un concepto erróneo**: el usuario creía algo incorrecto y ahora ve por qué. Son muy valiosos: predicen tropiezos futuros en temas relacionados.
4. **La misión cambió por lo aprendido**: el usuario descubrió que le importaba otra cosa. Enlaza con `MISION.md` y actualízalo.

### Qué no califica

- Material que solo se cubrió. Cubrir no es aprender. Espera la evidencia.
- Lo que ya está en `GLOSARIO.md` como definición. No dupliques.
- Bitácoras de actividad por sesión. Los registros no son un diario: son ideas que deciden.

## Reemplazo

Cuando un registro posterior contradice uno anterior (la comprensión del usuario se profundizó o se corrigió), marca el viejo con `Estado: reemplazado por LR-NNNN` en vez de borrarlo. La historia de cómo evolucionó la comprensión es en sí misma una señal útil.
