# Cambios

## 0.5.1 (2026-10-06)

Tras medir T17 (proteger el backend, 6,37 $, de los que 2,27 en Opus) y T33 (cambio de texto
sin flujo, 0,48 $).

- Sin flujo: las reglas pasan de director.md a kit-rules.md, que se carga siempre. En T33 el
  director no leyó su guía, editó estando en main y no pasó los tests. Ahora: rama antes de
  tocar nada, tests del componente al terminar, commit en la rama y documentos que citen lo
  cambiado en el mismo cambio.
- Navegador: siempre en un agente con sonnet, también cuando el usuario dice "hazlo tú". En T17
  el director hizo tres rondas con su propio contexto.
- Tablero: cada momento, en una sola edición por fichero. En T17 el cierre fueron ocho.
- El director no edita los tests de aceptación de test-writer.
- Al quedar una tarea lista para revisión, el director sugiere /clear antes de seguir.
- Respuestas de una línea cuando el usuario ejecuta comandos por su cuenta.
- Guía: hábitos que ahorran y mediciones de T17 y T33.

## 0.5.0 (2026-10-06)

Tras medir el contexto de arranque con /context: 41.000 tokens antes de escribir nada, de los
que 20.000 son herramientas de Claude Code y 4.200 eran las reglas del kit. Cada paso relee esa
base, así que el coste fijo depende sobre todo del número de pasos.

- Reglas comunes (`kit-rules.md`) reducidas a una página. Lo que solo necesita el director
  (modos, modelos, tablero, entorno, cierre) pasa a `.claude/kit/director.md`, y las reglas de
  tests y de specs a `.claude/kit/pruebas.md` y `.claude/kit/specs.md`. Se leen bajo demanda,
  así que los agentes dejan de cargarlas en cada llamada.
- Menos pasos del director: tablero en tres momentos (registro, aprobación y cierre) en lugar
  de tras cada paso, comandos agrupados, encargos con la lista de ficheros, y sin repetir build
  y tests en main tras una fusión fast-forward.
- Sin flujo: los cambios de pocas líneas los hace el director directamente, sin lanzar un
  agente.
- Preferencias por proyecto en `preferences` de project.json: tests, close_tests, mode, smoke,
  browser y max_criteria. Un project.json anterior sin esa clave usa los valores por defecto.
- Modo sin tests: "sin tests" en el encargo o `"tests": "none"`. Los tests existentes de los
  componentes tocados se siguen pasando al cerrar.
- Al cerrar solo se pasan los tests de los componentes tocados (`close_tests`).
- /resume se sitúa con el estado del repo (commits de spec, tests e implementación), ya que el
  tablero no anota cada paso.

## 0.4.0 (2026-10-06)

Tras medir una tarea mínima (T31, 0,98 $) y una de seguridad en modo completo (T32, 16,85 $,
de los que 14,99 fueron de agentes en Opus).

- Modelos en tareas de seguridad: la regla "no bajes de opus en nada que toque seguridad" hizo
  que todos los agentes corrieran en Opus, incluidos tests y pantallas. Ahora van con opus la
  spec, la revisión y el encargo con la lógica delicada; el resto, con sonnet.
- Tamaño: el director propone partir en dos features las tareas que necesitan más de tres
  encargos de desarrollo o añaden a la vez una pantalla y un servicio nuevos.
- Tareas muy pequeñas: el director avisa de que el flujo tiene un coste fijo y ofrece hacerlo
  sin flujo.
- Tablero: una línea por tarea, historial de una línea por tarea cerrada, archivo de las hechas
  en .claude/TASKS-archivo.md, y edición solo con la herramienta de edición. Motivo: un sed
  reescribió siete filas del historial, y el tablero largo se paga en cada tarea.
- a_markdown.py lee PDF (con pypdf), para cuando el lector de PDF de Claude Code falla.
- Guía: mediciones de T31 y T32.

Comprobado en Claude Code con la 0.3.0: aviso del modelo de la sesión, pregunta por el
navegador, hallazgos de revisión listados, Opus lanzado desde una sesión en Sonnet.

## 0.3.0 (2026-10-06)

Tras medir tres tareas en RENEUMA: completo con director en Opus (más de 2 $), ligero con
director en Opus (6,01 $, de los que 4,02 fueron del director) y ligero con director en Sonnet
(1,16 $). Conclusión: pesa más qué modelo lee, y con cuánto contexto, que el número de agentes.

- Tabla de modelos explícita (opus, sonnet, haiku), independiente del modelo de la sesión.
  Antes decía "el de la sesión" para lo delicado, y con la sesión en Sonnet eso bajaba de modelo
  justo donde no debía.
- "El modelo de la sesión": al empezar un flujo, el director dice con qué modelo corre y sugiere
  `/model sonnet` para lo rutinario. En modo completo lanza con opus lo que lo necesita.
- El director no revisa diffs de más de unos diez ficheros (lanza reviewer con sonnet) ni
  prueba en el navegador por su cuenta (pregunta, y si se quiere lo delega con sonnet).
- Aviso cuando una tarea pequeña se convierte en una refactorización, con la versión corta.
- El modelo de cada encargo se anota en el tablero y en el PR.
- Los hallazgos de la revisión no pueden desaparecer del resumen final.
- El smoke por "integración de un modelo" se refiere a un modelo real, no a un mock.
- `/feature`: el modo se anuncia antes de crear la rama o la spec.
- Guía: cómo medir el consumo y mediciones de referencia.

Comprobado en Claude Code: modo ligero, modo completo, elección de modelo por encargo y smoke.

## 0.2.1 (2026-10-06)

- Criterio de modo completo más estrecho. En la primera prueba, el director eligió completo
  para un backend que replicaba el de otro proceso, porque "añadía rutas a la API" e "integraba
  un modelo en mock". Ahora: completo solo si se cambian rutas o campos existentes, si se diseña
  una API sin patrón que copiar, si toca seguridad, si integra un modelo real o si cruza
  componentes con decisiones abiertas. Replicar un patrón existente va en ligero. En caso de
  duda, ligero.

## 0.2.0 (2026-10-06)

Para reducir el consumo: la prueba con RENEUMA gastó dos sesiones completas en tres tareas.

- `/feature` con dos modos. Ligero, por defecto: el director escribe una spec corta, un solo
  agente dev por componente hace código y tests críticos, y el director revisa el diff.
  Completo, a petición o cuando la tarea toca API, seguridad, modelos o cruza componentes con
  decisiones abiertas: spec-writer, test-writer, devs y reviewer.
- `/feature` acepta una spec ya escrita: la revisa contra el proyecto y sigue desde la
  aprobación.
- `/fix`: un solo agente dev escribe el test que reproduce el defecto, lo ve fallar y lo
  arregla. Reviewer solo en lo delicado.
- Modelo según la tarea: los agentes siguen heredando el de la sesión y el director elige en
  cada encargo con la tabla de kit-rules.md, lo dice y sube de modelo si el encargo sale mal.
- Specs cortas: de cinco a ocho criterios, detalles como notas de implementación, menos
  preguntas, cada criterio con su forma de comprobación (test, smoke o manual).
- Tests solo de lo crítico: rutas del backend, integración de modelos, seguridad y dos o tres
  por pantalla. Lo demás, a la lista "Comprobar a mano" del PR.
- `smoke.py`: conectividad con el stack levantado (URLs, puertos y llamadas de extremo a
  extremo), definida en `run.health` de project.json.

Sin probar en Claude Code: el modo ligero y la elección de modelo por encargo. Ver el paso 2.10
del plan.

## 0.1.3 (2026-10-06)

Tras probar el frontend en RENEUMA (T10). Incluye todo lo de la 0.1.2.

- Reglas del kit en `.claude/kit-rules.md`, que es del kit y se actualiza con `--update`.
  `CLAUDE.md` solo guarda lo propio del proyecto y lo importa. El instalador avisa si el
  `CLAUDE.md` es anterior y dice cómo migrarlo.
- Hooks: se bloquea escribir fuera del proyecto y de sus componentes, con Edit/Write y con
  `>`, `>>`, `cp`, `mv`, `tee` y `touch` hacia rutas absolutas. Motivo: un agente dejó un
  fichero en `C:\Program Files\Git\`.
- Agentes: los temporales van solo a `.claude/tmp/`. `test-writer` lista los detalles que la
  spec deja abiertos en lugar de decidirlos.
- `spec-writer`: criterios proporcionados al tamaño de la tarea, sin criterios de proceso, y
  detalles de pantalla cerrados antes de aprobar.
- `/adopt`: si no hay compose, lo dice y propone la tarea de crearlo a partir de un proyecto de
  referencia. Regla para las tareas de entorno.
- Cierre: se indican los criterios que quedan para comprobar a mano.

Comprobado en Windows: frontend-dev y tests con bUnit.
Sin probar en Windows: el bloqueo de escrituras fuera del proyecto y la importación de
kit-rules.md.

## 0.1.2 (2026-10-05)

Compose. Los proyectos reales se levantan con compose y la reducción lo había dejado fuera.

- `/adopt`: detecta ficheros compose y Dockerfile, servicios, puertos y .env, y anota en
  project.json (`run.up`, `run.down`, `run.health`) cómo se levanta el proyecto.
- `project.json` (plantilla): campo `run`.
- `CLAUDE.md` (plantilla): sección "Entorno local" y paso nuevo en el cierre: si la tarea toca
  Dockerfile, compose, dependencias o un modelo, se levanta el stack y se comprueba antes de
  cerrar, con permiso del usuario. Solo afecta a instalaciones nuevas.
- Plantilla del PR: casilla del contenedor.
- Los tests siguen pasándose en local; compose no se usa para los tests.

## 0.1.1 (2026-10-05)

Ajustes tras la primera prueba completa con el proyecto ficticio RENEUMA.

- `/fix`: si no hay defecto que reproducir, lo dice y propone una tarea chore con un solo agente.
- `/adopt`: pregunta por el remoto y deja anotado cómo se cierran las tareas.
- `CLAUDE.md` (plantilla): el cierre no intenta push si el proyecto no tiene remoto; línea nueva
  "Remoto y cierre de tareas". Solo afecta a instalaciones nuevas: en un proyecto ya instalado,
  pídele al director que lo anote.
- `backend-dev`, `reviewer` y plantilla de `CLAUDE.md`: el mock cambia con las entradas de forma
  artificial y declarada.
- `/feature`: responder a las preguntas no es aprobar la spec.
- Guía y plan: variable de entorno de Windows en lugar del perfil de PowerShell; cómo ver el
  tablero; estado de lo probado.

Comprobado en Windows dentro de Claude Code: instalación, carga de agentes y comandos, bloqueo
de los hooks, /adopt, /feature de backend y /resume.
Sin probar todavía: /fix con un defecto real y frontend-dev.

## 0.1.0 (2026-10-05)

Primera versión, reducida a lo necesario para empezar.

- Agentes: spec-writer, test-writer, backend-dev, frontend-dev, reviewer.
- Comandos: /adopt, /feature, /fix, /resume.
- Hooks: guard_commands.py (ramas protegidas, etiquetas, releases, push forzado) y
  guard_paths.py (.github/ y componentes de solo lectura).
- a_markdown.py para leer plantillas en Excel y Word.
- install.py con --role, --exclude-local, --update y --dry-run.

Probado: los tests del kit (pytest) en Linux con Python 3.
Sin probar todavía: dentro de Claude Code y en Windows. Ver el plan de puesta en marcha.
