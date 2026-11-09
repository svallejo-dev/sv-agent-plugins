# Reglas para contribuir a sv-agent-plugins

Este archivo es para quien edita este repositorio, persona o agente. Para usar los plugins en otro proyecto, la plantilla de AGENTS.md está en `plugins/general/skills/por-donde-empiezo/references/plantilla-AGENTS.md`, y la skill `por-donde-empiezo` la instala.

Responde y escribe en español; conserva en inglés los términos técnicos habituales.

## Estructura

- `plugins/<plugin>/skills/<skill>/SKILL.md`: una carpeta por skill, con `references/`, `scripts/` o `agents/` si los necesita.
- `catalogo.json`: **fuente única** de nombres, versiones, descripciones y categorías de los plugins.
- Manifiestos (`plugin.json`, `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.agents/plugins/`, `.github/plugin/`): **generados**. No se editan a mano; se regeneran con `python3 tools/build_manifests.py`.
- `install.sh`: instalación de skills sueltas (Windsurf y cualquier carpeta de skills).
- `plantillas/reglas-globales.md` y `tools/instalar-reglas-globales.sh`: reglas de comportamiento personales, conectadas con el archivo global de cada herramienta. No son parte de ningún plugin. La plantilla debe quedar por debajo de 6 000 caracteres (límite de Windsurf).
- `docs/CONTRATO-LENGUAJES.md`: el contrato `<lenguaje>-<rol>` entre `ingenieria` y los plugins de lenguaje.

## Reglas de las skills

1. **Estándar Agent Skills.** Frontmatter con solo `name` (igual a la carpeta), `description` entre comillas dobles y `license: MIT`. Ningún campo propio de una herramienta (por ejemplo, nada de `disable-model-invocation`).
2. **Nombres únicos en todo el repositorio**, con prefijo cuando el nombre es genérico (`qa-verify`, `go-testing`). Codex, Copilot, Cursor y Windsurf instalan las skills en carpetas planas, sin el prefijo del plugin.
3. **Referencias entre skills por nombre a secas** (`tdd`), nunca `plugin:skill`.
4. **Autocontenidas.** Los archivos compartidos viven en una skill hermana (como `qa-core`) y se enlazan con rutas relativas (`../qa-core/...`). Nunca en carpetas del plugin fuera de `skills/`.
5. **Neutrales respecto de la herramienta.** Si una skill usa sub-agentes, preguntas con opciones o carga otras skills, dice qué hacer cuando la herramienta no lo ofrece (ver `plugins/qa/skills/qa-core/referencias/portabilidad.md`).
6. **Skills exclusivas del usuario**: la descripción lo dice ("Úsala solo cuando el usuario la pida explícitamente") y la carpeta lleva `agents/openai.yaml` con `policy.allow_implicit_invocation: false` para Codex. No se lo pongas a una skill que otra debe poder activar por su descripción.
7. Cada skill se valida con `agentskills validate plugins/<plugin>/skills/<skill>` (`pip install skills-ref`).

## Versiones: sin subir versión no hay actualización

Claude Code, Codex y Copilot guardan cada plugin por número de versión. **Si cambias cualquier archivo de un plugin y no subes su versión en `catalogo.json`, nadie recibe el cambio.** Comprobado: `claude plugin update` responde "already at the latest version".

- Corrección → parche (`0.2.0` → `0.2.1`); skill nueva o cambio de comportamiento → menor (`0.3.0`); renombrar o quitar una skill → menor mientras estemos en `0.x`, y anótalo en el commit.
- Después: `python3 tools/build_manifests.py`.
- La CI lo comprueba con `python3 tools/check_versions.py --base origin/main`.

## Antes de hacer commit

```bash
python3 tools/build_manifests.py --check
python3 tools/check_versions.py --base origin/main
for d in plugins/*/skills/*/; do agentskills validate "$d"; done
python3 -m unittest discover -s plugins/qa/skills/qa-core/scripts/tests
python3 -m unittest discover -s plugins/arquitectura/skills/capacity-estimation/scripts -p 'test_*.py'
claude plugin validate .
```

Para probar un plugin sin instalarlo ni subir versión: `claude --plugin-dir ./plugins/<plugin>`.

## Atribución

`general` y la mayor parte de `ingenieria` se adaptaron de mattpocock/skills, y `building-blocks` de proyecto26/system-design-skills, ambos con licencia MIT. Al adaptar contenido de terceros, cítalo en el README del plugin y en `LICENSE`.
