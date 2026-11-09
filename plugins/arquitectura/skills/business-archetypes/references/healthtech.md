# Healthtech

**Analogía:** un archivo clínico con portero. Lo importante no es la velocidad de los pasillos, sino que solo entre quien debe, que quede registrado quién miró qué y que el expediente nunca se pierda ni se mezcle.

## Fuerzas dominantes

- **Privacidad y regulación de datos de salud**: HIPAA en Estados Unidos; en Colombia, la Ley 1581 de 2012 de protección de datos personales y la normativa de historia clínica. Verifica la regulación vigente de cada país.
- **Auditoría y consentimiento**: quién accedió a qué dato, cuándo y con qué permiso del paciente.
- **Integración con terceros clínicos**: aseguradoras, laboratorios, prestadores, con estándares como HL7 FHIR y sistemas legacy.
- **Disponibilidad en flujos críticos** (telemedicina, prescripciones), aunque el volumen sea moderado.

## Forma de la carga (sin métricas)

- Volumen moderado, con picos en horarios de atención y campañas (vacunación, temporadas de enfermedades respiratorias).
- Media pesada en algunos flujos (imágenes, videoconsultas).
- Escenarios para explorar: 1k, 100k y 10M pacientes registrados, con una fracción pequeña activa a la vez.

## Invariantes y consistencia

- Ningún dato clínico accesible sin autorización; mínimo privilegio y consentimiento explícito.
- Registro de auditoría inmutable de accesos y cambios.
- La historia clínica no se sobrescribe: se versiona y se anota.
- Identidad del paciente correcta (evitar mezclar historias de dos personas).

## Subdominios típicos

- **Core**: el servicio de salud que da valor (telemedicina, gestión de pacientes, triage, programas de cuidado).
- **Supporting**: agenda y citas, historia clínica, facturación a aseguradoras, interoperabilidad.
- **Generic**: videollamadas, mensajería, identidad, almacenamiento cifrado.

## Camino recorrido (verifica antes de citar)

- HL7 FHIR como estándar de interoperabilidad de datos clínicos.
- Cifrado en reposo y en tránsito, con gestión de llaves y segregación de datos sensibles.
- Separar los datos identificables de los datos clínicos (seudonimización) para analítica.

## Modos de fallo típicos (semilla para el red team)

- Acceso indebido a datos por permisos demasiado amplios o por un endpoint sin control.
- Logs o métricas que filtran datos de salud.
- Integración con un tercero clínico caída en un flujo crítico.
- Mezcla de historias por un error de identidad del paciente.
- Videoconsultas que se degradan en horas pico.

## Preguntas que cambian el diseño

- ¿Qué regulación aplica en cada país donde opera el producto?
- ¿Qué datos son clínicos y cuáles administrativos? ¿Quién puede ver cada uno?
- ¿Con qué terceros hay que integrarse y con qué estándar?
- ¿Qué flujos son críticos para la seguridad del paciente?

## Hipótesis para un PoC

- Validar el modelo de permisos y consentimiento con casos negativos (quién no debe ver qué).
- Validar la integración con el tercero clínico más crítico en su entorno de pruebas.
- Instrumentar sin datos sensibles: auditoría de accesos, latencia de flujos críticos, errores de integración. Diseñar la telemetría para que nunca contenga datos de salud.
