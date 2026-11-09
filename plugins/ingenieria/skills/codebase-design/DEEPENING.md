# Profundizar

Cómo profundizar con seguridad un grupo de módulos superficiales según sus dependencias. Asume el vocabulario de [SKILL.md](SKILL.md): **módulo**, **interfaz**, **seam**, **adapter**.

## Categorías de dependencias

Al evaluar un candidato, clasifica sus dependencias. La categoría decide cómo se testea el módulo profundizado a través de su seam.

### 1. En proceso

Cómputo puro, estado en memoria, sin I/O. Siempre se puede profundizar: fusiona los módulos y testea directamente a través de la interfaz nueva. No hace falta adapter.

### 2. Sustituible localmente

Dependencias con un sustituto local para test: Postgres o MySQL en un contenedor, Redis o Kafka en contenedor, un filesystem en memoria o un directorio temporal. Se puede profundizar si existe el sustituto. El módulo profundizado se testea con el sustituto corriendo en la suite. El seam es interno; no hay port en la interfaz externa del módulo.

### 3. Remota pero propia (Ports & Adapters)

Tus propios servicios al otro lado de la red (microservicios, APIs internas, colas). Define un **port** (una interfaz) en el seam. El módulo profundo es dueño de la lógica; el transporte se inyecta como **adapter**. Los tests usan un adapter en memoria; producción usa un adapter HTTP, gRPC o de cola.

Forma de la recomendación: _"Define un port en el seam, implementa un adapter HTTP para producción y uno en memoria para tests, así la lógica vive en un único módulo profundo aunque se despliegue a través de la red."_

### 4. Externa de verdad (doble)

Servicios de terceros que no controlas (pasarelas de pago, partners, proveedores de identidad). El módulo profundizado recibe la dependencia externa como un port inyectado; los tests usan un adapter falso o un servidor HTTP local que imita al tercero.

## Disciplina de seams

- **Un adapter significa un seam hipotético. Dos adapters significan uno real.** No introduzcas un port si no se justifican al menos dos adapters (normalmente producción + test). Un seam con un solo adapter es solo indirección.
- **Seams internos vs externos.** Un módulo profundo puede tener seams internos (privados, usados por sus propios tests) además del seam externo de su interfaz. No expongas seams internos en la interfaz solo porque los tests los usan.

## Estrategia de testing: reemplaza, no apiles

- Los tests unitarios viejos sobre módulos superficiales sobran cuando existen tests en la interfaz del módulo profundizado; bórralos.
- Escribe tests nuevos en la interfaz del módulo profundizado. **La interfaz es la superficie de test.**
- Los tests asertan resultados observables a través de la interfaz, no estado interno.
- Los tests sobreviven a refactors internos porque describen comportamiento, no implementación. Si un test tiene que cambiar cuando cambia la implementación, está testeando más allá de la interfaz.
