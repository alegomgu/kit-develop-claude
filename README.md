# idener-claude-kit

Kit mínimo para trabajar con Claude Code en las plataformas de proyectos de Idener: cinco
agentes, cuatro comandos, dos barreras automáticas (hooks) y un instalador. `/feature` trabaja
en modo ligero por defecto y en modo completo cuando la tarea lo merece.

La explicación completa está en `docs/guia-multiagente-idener.md` y los pasos para ponerlo en
marcha en `docs/plan-puesta-en-marcha.md`.

## Uso rápido

```powershell
# comprobar el kit (una vez)
python -m pytest

# instalar en un repo, sin dejar rastro en git
python install.py "C:\ruta\al\repo" --exclude-local

# actualizar un repo ya instalado tras cambiar el kit
python install.py "C:\ruta\al\repo" --update --exclude-local
```

Después, dentro del repo: `claude` y `/adopt`.

## Contenido

| Carpeta | Qué hay |
|---|---|
| `agents/` | spec-writer, test-writer, backend-dev, frontend-dev, reviewer |
| `skills/` | /adopt, /feature, /fix, /resume |
| `scripts/` | guard_commands.py y guard_paths.py (hooks), a_markdown.py (Excel y Word a Markdown), smoke.py (conectividad) |
| `templates/` | kit-rules.md (reglas comunes, cortas), kit/ (guía del director, pruebas y specs, leídas bajo demanda), CLAUDE.md, TASKS.md, project.json, settings.json, spec.md, pr.md |
| `tests/` | tests del kit (`python -m pytest`) |
| `docs/` | la guía y el plan de puesta en marcha |

Este kit es la única fuente de los agentes y los comandos: se cambian aquí y se llevan a cada
proyecto con `--update`. Las ideas de mejora se apuntan en `PROPUESTAS.md`.
