# Diséñalo dos veces

Cuando el usuario quiera explorar interfaces alternativas para un candidato a profundizar, usa este patrón de sub-agentes en paralelo. Basado en "Design It Twice" (Ousterhout): tu primera idea rara vez es la mejor.

Usa el vocabulario de [SKILL.md](SKILL.md): **módulo**, **interfaz**, **seam**, **adapter**, **leverage**.

## Proceso

### 1. Enmarca el espacio del problema

Antes de lanzar sub-agentes, escribe para el usuario una explicación del espacio del problema del candidato elegido:

- Las restricciones que cualquier interfaz nueva debe cumplir
- Las dependencias de las que dependería y en qué categoría cae cada una (ver [DEEPENING.md](DEEPENING.md))
- Un esbozo de código ilustrativo en el lenguaje del proyecto para aterrizar las restricciones (no una propuesta, solo una forma de concretarlas)

Muéstraselo al usuario y pasa de inmediato al paso 2. El usuario lee y piensa mientras los sub-agentes trabajan en paralelo.

### 2. Lanza los sub-agentes

Lanza 3 o más sub-agentes en paralelo, cada uno con contexto limpio. Cada uno debe producir una interfaz **radicalmente distinta** para el módulo profundizado.

> **Portabilidad:** si tu herramienta no tiene sub-agentes, ejecuta cada encargo en una conversación nueva con solo su brief, o en secuencia en esta sesión, y declara en el resultado que no hubo aislamiento de contexto.

Dale a cada sub-agente un brief técnico propio (rutas de archivos, detalles de acoplamiento, categoría de dependencias según [DEEPENING.md](DEEPENING.md), qué queda detrás del seam). El brief es independiente de la explicación del paso 1. Dale a cada uno una restricción de diseño distinta:

- Agente 1: "Minimiza la interfaz: entre 1 y 3 puntos de entrada como máximo. Maximiza el leverage por punto de entrada."
- Agente 2: "Maximiza la flexibilidad: soporta muchos casos de uso y extensión."
- Agente 3: "Optimiza para el llamador más común: haz trivial el caso por defecto."
- Agente 4 (si aplica): "Diseña con ports & adapters para las dependencias que cruzan el seam."

Incluye en el brief el vocabulario de [SKILL.md](SKILL.md) y el de `GLOSARIO.md`, para que cada sub-agente nombre las cosas de forma consistente con el lenguaje de arquitectura y con el del dominio. Pide que el código sea idiomático en el lenguaje del proyecto; si cargaste `<lenguaje>-design`, incluye sus reglas en el brief.

Cada sub-agente entrega:

1. Interfaz (tipos, funciones, métodos, parámetros, más invariantes, orden y modos de error)
2. Ejemplo de uso desde un llamador
3. Qué esconde la implementación detrás del seam
4. Estrategia de dependencias y adapters (ver [DEEPENING.md](DEEPENING.md))
5. Trade-offs: dónde el leverage es alto y dónde es pobre

### 3. Presenta y compara

Presenta los diseños uno a uno para que el usuario los asimile, después compáralos en prosa. Contrasta por **profundidad** (leverage en la interfaz), **locality** (dónde se concentran los cambios) y **ubicación del seam**.

Tras comparar, da tu recomendación: qué diseño crees que es el más fuerte y por qué. Si elementos de varios diseños combinan bien, propón un híbrido. Sé opinativo: el usuario quiere una lectura firme, no un menú.
