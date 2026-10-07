# Guía: trabajar con agentes en Claude Code (Idener)

> Versión 0.17 (reducida) · 2026-10-06 · Kit 0.5.1
>
> Sustituye a la versión 0.7. Aquella describía un kit grande que no llegó a construirse; esta
> describe el kit mínimo que ya existe (`idener-claude-kit`). Lo aplazado está en el §12.

## Chuleta

| Quiero | Hago |
|---|---|
| Instalar el kit en un repo | `python "$env:IDENER_KIT\install.py" <repo> --exclude-local` |
| Preparar el proyecto (una vez) | Dentro de `claude`: `/adopt` |
| Añadir una funcionalidad | `/feature <descripción, fichero o URL>` (modo ligero) |
| Lo mismo, con todos los controles | `/feature <...> completo` |
| Usar una spec escrita fuera | `/feature docs/specs/<fichero>.md` |
| Encargo rápido a un solo agente | «Sin flujo: encárgale a backend-dev…» |
| Comprobar la conectividad | Con el stack levantado: `python .claude\scripts\smoke.py` |
| Arreglar un fallo | `/fix <descripción del fallo>` |
| Retomar tras limpiar el contexto | `/clear` y luego `/resume` |
| Preguntar, explorar, cambio trivial | Se lo pido al chat sin ningún comando |
| Llevar un cambio del kit a un proyecto | `python "$env:IDENER_KIT\install.py" <repo> --update --exclude-local` |

---

## 1. Qué es y cuándo usarlo

Un conjunto pequeño de ficheros que se copian en un repo para que Claude Code trabaje siempre
igual: una spec corta que tú apruebas, el código con los tests de lo crítico, una revisión y un
PR preparado que tú fusionas.

Hay tres formas de pedir trabajo, de menos a más coste:

| Forma | Qué hace | Para qué |
|---|---|---|
| Al chat, sin comando | Lo que pidas, con los hooks activos | Preguntas, exploración, textos, estilos, limpiezas, algo parecido a lo que ya existe |
| `/feature` (modo ligero) | Spec corta, tu aprobación, un agente por componente y revisión del director | La mayoría de funcionalidades |
| `/feature … completo` | Spec con `spec-writer`, tests escritos aparte, devs y `reviewer` | Cambios en rutas o campos que ya existen, API nueva sin patrón que copiar, seguridad, integración de un modelo real, lo que cruza backend y frontend con decisiones abiertas |

El director elige entre ligero y completo y te dice por qué; puedes cambiarlo. Lo que replica
un patrón que ya existe (el mismo backend para otro proceso, otra página igual) va en ligero
aunque añada rutas; un mock no cuenta como integrar un modelo. La regla práctica:
si puedes describir el resultado en un párrafo y sabes comprobarlo a ojo, pídelo directo; si al
escribir el encargo te salen dudas, usa `/feature`.

## 2. Qué trae el kit

| Pieza | Qué es | Para qué |
|---|---|---|
| `spec-writer` | Agente | Convierte la petición y sus fuentes en una spec con criterios de aceptación |
| `test-writer` | Agente | Escribe los tests antes que el código |
| `backend-dev` | Agente | Implementa en el backend (FastAPI) |
| `frontend-dev` | Agente | Implementa en el frontend (Blazor) |
| `reviewer` | Agente | Compara los cambios con la spec; no modifica nada |
| `/adopt` | Comando | Deduce cómo es el proyecto, una vez |
| `/feature` | Comando | Funcionalidad nueva, de la idea al PR |
| `/fix` | Comando | Defecto: test que lo reproduce y cambio mínimo |
| `/resume` | Comando | Retoma el trabajo en una sesión limpia |
| `guard_commands.py` | Hook | Impide commits en `main`, etiquetas, releases y push forzado |
| `guard_paths.py` | Hook | Impide escribir en `.github/`, en componentes de solo lectura y fuera del proyecto |
| `a_markdown.py` | Script | Pasa un Excel o un Word a Markdown para que lo lean los agentes |
| `smoke.py` | Script | Comprueba la conectividad con el stack levantado: frontend, backend y base de datos |
| `install.py` | Instalador | Copia todo lo anterior a un repo y lo deja fuera de git |

Conceptos, por si no los conoces:

- **Sesión principal o director:** el chat de Claude Code con el que hablas. Reparte el trabajo.
- **Agente (subagente):** un Claude aparte que el director lanza para una tarea concreta. Trabaja
  en su propio contexto y devuelve solo un resumen. Son ficheros en `.claude/agents/`.
- **Comando (skill):** una receta de pasos que el director sigue cuando escribes `/nombre`. Son
  ficheros en `.claude/skills/`.
- **Hook:** un script que Claude Code ejecuta solo antes de usar una herramienta. Si el script
  dice que no, la acción no se hace. No depende del modelo.

## 3. Requisitos

| Qué | Para qué | Cómo comprobarlo |
|---|---|---|
| Git | Todo | `git --version` |
| Python 3.10 o superior, como `python` | Instalador y hooks | `python --version` |
| Claude Code | Todo | `claude --version` |
| `openpyxl` | Leer plantillas en Excel | `python -c "import openpyxl"` |
| `pytest` | Probar el kit (solo una vez) | `python -m pytest --version` |
| SDK de .NET | Proyectos con frontend Blazor | `dotnet --version` |

`gh` (la herramienta de GitHub) es opcional: sin ella, el texto del PR queda preparado para
pegarlo en la web.

## 4. Poner el kit en tu equipo

1. Descomprime `idener-claude-kit.zip` en `Escritorio\2026\`. Debe quedar la carpeta
   `Escritorio\2026\idener-claude-kit\` con `install.py` dentro.
2. Abre PowerShell en esa carpeta y comprueba el kit:
   ```powershell
   python -m pytest
   ```
   Deben pasar todos los tests. Si alguno falla, no sigas: apúntalo y revísalo.
3. Guarda la ruta del kit en una variable de entorno de Windows para no escribirla cada vez.
   Ejecuta esto una sola vez, con tu ruta real:
   ```powershell
   [Environment]::SetEnvironmentVariable("IDENER_KIT", "C:\Users\Idener\OneDrive - Idener.es Directory\Escritorio\2026\idener-claude-kit", "User")
   ```
   Cierra y abre PowerShell. `echo $env:IDENER_KIT` debe enseñar la ruta. No se usa el perfil
   de PowerShell porque en los equipos de la empresa los scripts sin firmar están bloqueados.
4. Opcional: `git init` dentro de la carpeta del kit para guardar el historial de sus cambios.
   Sin remoto.

## 5. Instalar el kit en un proyecto

El destino tiene que ser un repo git (una carpeta con `.git`).

**Un solo repo:**
```powershell
cd "C:\ruta\al\repo"
python "$env:IDENER_KIT\install.py" . --exclude-local
git status
```

**Proyecto en varios repos** (backend y frontend separados): el kit completo va en el backend y
el frontend solo recibe una nota que remite a él.
```powershell
python "$env:IDENER_KIT\install.py" .\metallico-backend --exclude-local
python "$env:IDENER_KIT\install.py" .\metallico-frontend --role secondary --exclude-local
cd metallico-backend
claude --add-dir ..\metallico-frontend
```

Opciones:

| Opción | Efecto |
|---|---|
| `--exclude-local` | Las exclusiones van a `.git/info/exclude`: el repo no cambia en nada. Sin ella van al `.gitignore`, que sí es un cambio visible |
| `--role secondary` | Repo adicional de un proyecto con varios repos |
| `--update` | Actualiza un repo ya instalado (§10) |
| `--dry-run` | Enseña lo que haría sin tocar nada |

Qué crea:

| Fichero | De quién es | Al actualizar |
|---|---|---|
| `.claude/agents/`, `.claude/skills/`, `.claude/scripts/`, `.claude/templates/` | Del kit | Se sustituye |
| `.claude/kit-rules.md` | Del kit: las reglas comunes, cortas. Se cargan en cada sesión y en cada agente | Se sustituye |
| `.claude/kit/` | Del kit: guía del director, qué se prueba y cómo se escribe una spec. Se leen solo cuando hacen falta | Se sustituye |
| `.claude/settings.json` | Los `hooks`, del kit; los `permissions`, tuyos | Solo cambian los hooks |
| `.claude/project.json` | Del proyecto | Se conserva |
| `CLAUDE.md` | Del proyecto: qué es, convenciones y trampas. Importa `kit-rules.md` | Se conserva |
| `TASKS.md` | Del proyecto | Se conserva |

Nada de esto se versiona. Tras instalar, `git status` no debe enseñar nada nuevo (con
`--exclude-local`).

**Desinstalar:** borra `.claude/`, `CLAUDE.md` y `TASKS.md`.

## 6. La primera vez en un proyecto: `/adopt`

1. En PowerShell, dentro del repo: `claude`. Si pregunta si confías en la carpeta, di que sí.
2. Comprueba que el kit se ha cargado: al escribir `/` deben aparecer `adopt`, `feature`, `fix`
   y `resume`; al escribir `@` y empezar a teclear `rev`, el agente `reviewer`.
3. Escribe `/adopt` y pulsa Intro.
4. Claude mira el repo y te propone: componentes y sus rutas, los comandos de build y test, cómo
   se levanta el proyecto con compose (servicios, puertos y URLs de comprobación), los
   documentos de referencia por orden de autoridad, las convenciones de ramas y commits, y los
   huecos que vea. **No cambia nada del proyecto**: solo rellena `.claude/project.json`,
   `CLAUDE.md` y `TASKS.md`.
5. Lee lo que propone y corrígelo hablando con él. Fíjate sobre todo en los comandos de test y en
   qué componentes marca como de solo lectura.
6. Si el proyecto no tiene compose, te lo dice y propone una tarea para crearlo, copiando las
   convenciones de un proyecto de referencia que le indiques. No lo crea por su cuenta.
7. Si el repo no tiene remoto te pregunta si lo tendrá, y deja anotado cómo se cierran las
   tareas: con push y PR, o solo con el texto del PR preparado.

## 7. El día a día

Durante el trabajo Claude pide permiso para ejecutar comandos y editar ficheros. Puedes aceptar
uno a uno o «permitir siempre» los que veas seguros.

### 7.1. `/feature`

```
/feature Exportar los resultados de la simulación a Excel
/feature docs/fuentes/plantilla_pirolisis.xlsx backend con mock del proceso
/feature Autenticación con Identity y usuarios en Postgres completo
/feature docs/specs/T14-exportacion.md
```

**Modo ligero** (por defecto):

| Paso | Quién | Qué pasa | Qué haces tú |
|---|---|---|---|
| 1–3 | Director | Lee la entrada, elige el modo y te lo dice, apunta la tarea y crea la rama | Cambiar el modo si no estás de acuerdo |
| 4 | Director | Escribe una spec corta: de cinco a ocho criterios y unas notas | Nada |
| 5 | Director | Te pregunta solo lo que cambia el resultado o toca la API | **Responder** |
| 6 | Director | Te enseña la spec | **Leer y aprobar** |
| 7 | Un dev por componente | Código y tests de lo crítico | Nada |
| 8 | Director | Ejecuta él build y tests y mira el ámbito | Nada |
| 9 | Director | Revisa el diff contra los criterios | Nada, salvo que escale |
| 10 | Director | Smoke si toca, commit, push y texto del PR | **Probar a mano lo que te indique y fusionar** |

**Modo completo:** igual, pero la spec la escribe `spec-writer`, los tests los escribe
`test-writer` antes que el código y la revisión la hace `reviewer`, con dos vueltas como mucho.
Los cambios en la API se aprueban aparte.

**Spec escrita fuera:** si le pasas una spec ya hecha, no la reescribe. La revisa contra el
código, te dice qué no encaja y sigue desde la aprobación.

El paso de aprobación es el importante: lo que apruebes es lo que se construye. Una spec corta
se lee entera; por eso son cortas.

### 7.2. `/fix`

```
/fix El endpoint de simulación devuelve 500 cuando tyre_type es "truck"
```

1. El director busca cuál es el comportamiento correcto en specs, contrato y tests. Si no está
   escrito, **te lo pregunta**. Si lo que pides es cambiar el comportamiento, te propone
   `/feature`.
2. Apunta la tarea y crea la rama.
3. Un agente dev escribe el test que reproduce el fallo, lo ejecuta para verlo fallar, hace el
   cambio mínimo y deja los tests en verde.
4. El director comprueba que el test existe y que fallaba por el motivo descrito, y ejecuta él
   los tests.
5. El director revisa el diff. `reviewer` solo interviene si el fix toca seguridad, la API o un
   modelo.
6. Commit, push y texto del PR. **Tú fusionas.**

Si lo que pides no es un defecto (una limpieza, un refactor, un comentario), el director te lo
dice y propone hacerlo como tarea `chore`. Para retoques triviales es más barato pedirlo sin
ningún comando.

### 7.3. `/resume`

Cuando la conversación se alarga, las respuestas empeoran. Escribe `/clear` para vaciar el
contexto y luego `/resume`: lee el tablero y git, mira en qué paso iba la tarea y continúa desde
ahí. No se pierde nada porque el estado está en `TASKS.md`, en la spec y en la rama.

Úsalo también al empezar el día.

### 7.4. Compose

Los tests se pasan en local. Compose sirve para levantar la plataforma y comprobar que arranca.
`/adopt` anota en `project.json` (`run`) cómo se levanta, cómo se para y qué URLs deben
responder.

Cuando una tarea toca un Dockerfile, un fichero compose, dependencias o la integración de un
modelo, el director te pide permiso, levanta el stack, comprueba esas URLs y lo para antes de
cerrar la tarea. Si no arranca, la tarea no se cierra. Levantar y parar contenedores siempre
pide tu confirmación.

### 7.5. Qué se prueba

Se prueba lo crítico, no todo. Un test por criterio ya no es la regla.

| Qué | Tests automáticos |
|---|---|
| Cada ruta del backend | Caso normal, un error de validación con su campo y forma de la respuesta |
| Integración de un modelo | Unidades, valores por defecto y aislamiento entre dos peticiones seguidas |
| Seguridad | Sin sesión se rechaza; con un rol que no corresponde se rechaza |
| Cada pantalla | Dos o tres como mucho, de lo que es fácil que falle |
| Un fix | El test que reproduce el defecto |

No se escriben tests de etiquetas, textos, atributos ni menús. Eso va a la lista «Comprobar a
mano» del PR.

La conectividad entre frontend, backend y base de datos se comprueba con el stack levantado y
`smoke.py`, que lee de `project.json` (`run.health`) qué debe responder: URLs, puertos
(`tcp://localhost:5432`) y, si quieres, una llamada completa de extremo a extremo. El director lo
ejecuta al cerrar las tareas que tocan contenedores, dependencias, base de datos, autenticación,
modelos o la comunicación entre frontend y backend.

El coste de probar menos: lo que no tiene test puede romperse sin avisar cuando alguien toque ese
código más adelante. Con las rutas cubiertas, el riesgo queda en la interfaz, que se comprueba a
ojo.

### 7.6. Modelos: el de la sesión y el de cada agente

**El modelo de la sesión es lo que más pesa en el coste.** El director relee todo el contexto en
cada paso. En las mediciones de RENEUMA (§7.8), una tarea con el director en Opus costó 6
dólares, de los que 4 fueron del director; una parecida con el director en Sonnet costó 1,16.

- Para el modo ligero, los fixes normales y las tareas de entorno, trabaja con la sesión en
  Sonnet: `/model` antes de empezar. Queda guardado como modelo por defecto.
- Si la sesión está en Opus y la tarea es rutinaria, el director te sugiere cambiar.
- En modo completo no hace falta subir la sesión: el director lanza con Opus los encargos que lo
  piden, aunque él corra en Sonnet.

**El modelo de cada agente lo elige el director** en cada encargo, y te lo dice:

| Tipo de trabajo | Modelo |
|---|---|
| Specs con decisiones abiertas, seguridad, modelos científicos reales, cambios en rutas o campos existentes, fallos difíciles, revisiones delicadas | opus |
| Implementar con spec clara o a partir de algo parecido, tests, entorno, revisión normal, comprobaciones en el navegador | sonnet |
| Trabajo mecánico: renombrar, textos, convertir documentos, buscar | haiku |

Si un encargo sale mal con un modelo, lo repite con el superior. Puedes imponer el tuyo en
cualquier momento.

En una tarea de seguridad no todo va con Opus. Van con Opus la spec, la revisión y el encargo que
implementa la lógica delicada (autorización en servidor, permisos, sesiones). Los tests, las
pantallas y el resto van con Sonnet. En la primera tarea de seguridad medida (§7.8) todo se
hizo con Opus y costó 15 de los 17 dólares.

El modelo de cada encargo queda anotado en «Notas» del tablero y en el PR. El dato real lo da
`/usage`, que desglosa el consumo de la sesión por modelo.

Otras tres reglas que ahorran:

- El director no revisa diffs grandes: por encima de unos diez ficheros lanza `reviewer`.
- El director no prueba en el navegador por su cuenta: al cerrar te pregunta si lo haces tú o lo
  quieres hecho, y en ese caso lo delega en un agente con Sonnet.
- Si una tarea pequeña se convierte en una refactorización al escribir la spec, te lo dice y te
  ofrece la versión corta.

### 7.7. Cómo medir el consumo

`/usage`, dentro de Claude Code, muestra los tokens y el coste estimado de la sesión, por
modelo. El contador se reinicia con `/clear`, así que para medir una tarea: `/clear` antes de
empezar y `/usage` al terminar, antes de limpiar otra vez. Con suscripción, el importe no es lo
que pagas, pero sirve para comparar tareas.

La barra de uso de la sesión y de la semana no vale para comparar tareas: es compartida con el
resto de lo que hagas con Claude en ese periodo.

### 7.8. Mediciones de referencia

Tomadas en RENEUMA el 2026-10-06, con los kits 0.2 y 0.3. Son tareas distintas, no la misma
repetida, así que sirven de orden de magnitud y no de comparación exacta.

| Tarea | Modo | Director | Coste | Tiempo de API | Tamaño |
|---|---|---|---|---|---|
| T28: backend simulado de desvulcanización | Completo | Opus | Más de 2,04 $ (medido a mitad) | Más de 6 min | 3 rutas, 15 tests nuevos |
| T29: página de desvulcanización, unificando el código con pirólisis | Ligero | Opus | 6,01 $ (4,02 del director) | 10 min 39 s | 43 ficheros, 4 tests nuevos, prueba en navegador |
| T30: descarga de resultados en CSV | Ligero | Sonnet | 1,16 $ | 4 min | 11 ficheros, 4 tests nuevos, sin navegador |
| T31: botón para restablecer valores por defecto | Ligero | Sonnet | 0,98 $ | 2 min 16 s | 7 ficheros, 4 tests nuevos |
| T32: roles y página de administración de usuarios | Completo | Sonnet, con todos los agentes en Opus | 16,85 $ (14,99 de los agentes) | 45 min 38 s | 42 ficheros, 2.400 líneas, 30 tests nuevos, smoke |
| T17: proteger el backend con una clave | Completo | Sonnet, con Opus solo en spec, backend y revisión | 6,37 $ (2,27 en Opus) | 16 min 59 s | 18 ficheros, 623 líneas, smoke y tres rondas en el navegador |
| T33: cambiar el texto de un botón | Sin flujo | Sonnet, sin agentes | 0,48 $ | 1 min 12 s | 2 ficheros, y después la documentación |

Tres cosas más que salen de T31 y T32:

- **Un `/feature` tiene un coste fijo de alrededor de un dólar**, haga lo que haga. Lo muy
  pequeño sale más barato sin flujo, y el director lo avisa.
- **Una tarea de seguridad grande cuesta en serio:** 17 dólares y media sesión del plan. La
  calidad fue alta (el revisor encontró una condición de carrera y un fallo de arranque que
  dejaba la plataforma sin administrador), pero casi todo el gasto fue de agentes en Opus
  haciendo también tests y pantallas.
- **El número de criterios no mide el tamaño.** T32 tenía ocho criterios y 2.400 líneas. Ahora
  el director propone partir las tareas que necesitan más de tres encargos de desarrollo.

**Lo que añadieron T17 y T33** (kit 0.5.0):

- El reparto de modelos funciona: en T17 Opus fue un tercio del coste, frente a casi todo en T32.
- El gasto se movió al director: 73 peticiones, por las pruebas en el navegador que hizo él
  mismo, las preguntas en la misma sesión y un cierre del tablero en ocho ediciones.
- Cada mensaje en una sesión cargada cuesta entre dos y cinco céntimos, diga lo que diga. T33
  fueron 20 mensajes para un cambio de dos líneas: el cambio costó poco y la conversación, el
  resto.
- Sin flujo, el director no leyó su guía: editó estando en `main` y no pasó los tests. Por eso
  la 0.5.1 lleva las reglas de «sin flujo» a las que se cargan siempre.

**De dónde sale el coste fijo.** `/context`, justo después de un `/clear`, mostró 41.000 tokens
ocupados antes de escribir nada. La mitad (20.000) son las herramientas de Claude Code, que no
dependen de nosotros; las reglas del kit eran 4.200 y `CLAUDE.md` 1.400. Cada paso del director
y cada llamada de cada agente relee al menos esa base. Un `/feature` mínimo son unas cuarenta o
cincuenta relecturas: de ahí el dólar. Por eso la 0.5.0 ataca el número de pasos (tablero en
tres momentos, comandos agrupados, cambios triviales hechos por el director sin lanzar un
agente) y deja las reglas que se cargan siempre en menos de una cuarta parte.

Lo que se aprendió antes: el número de agentes pesa poco; pesa qué modelo lee y con cuánto contexto.
El modo ligero con el director en Opus fue lo más caro. Con el director en Sonnet la calidad se
mantuvo en una tarea rutinaria: spec corta, decisiones señaladas, pregunta ante un test que
chocaba y comprobaciones hechas por él.

### 7.9. Hábitos que ahorran

- **Los comandos de git, en otra terminal.** Cada comando que lanzas con `!` dentro de Claude
  Code provoca una respuesta del director, que relee todo el contexto para decirte algo que ya
  sabes.
- **`/clear` cuando la tarea quede lista para revisión.** El estado está en el PR y en el
  tablero. Las comprobaciones y las preguntas posteriores salen más baratas en una sesión
  limpia.
- **Junta lo que vayas a pedir.** «Crea la rama, haz el commit y dime cómo fusionar» en un
  mensaje cuesta la tercera parte que en tres.
- **Las pruebas en el navegador, a un agente.** El director ya no las hace él aunque se lo
  pidas: las encarga, porque un agente arranca con un contexto mucho menor.

### 7.10. Sin flujo

«¿Dónde se calcula X?», «explícame este módulo», «cambia este texto»: se pide directamente. Los
hooks siguen activos aunque no uses ningún comando.

### 7.11. Preferencias del proyecto

Cuánto se hace de cada cosa se ajusta por proyecto, en `preferences` de `.claude/project.json`,
sin tocar el kit. Si falta una clave vale el primer valor. Lo que escribas en el encargo manda
sobre la preferencia para esa tarea.

| Clave | Valores |
|---|---|
| `tests` | `critical`: lo crítico (§7.5) · `none`: no se escriben tests nuevos · `full`: un test por criterio |
| `close_tests` | `touched`: al cerrar, solo los tests de los componentes tocados · `all`: los de todos |
| `mode` | `auto`: el director elige · `light` · `full` |
| `smoke` | `ask`: pide permiso cuando toca · `never` |
| `browser` | `ask`: pregunta al cerrar · `user`: siempre tú · `agent`: siempre un agente |
| `max_criteria` | `8`: tope de criterios por spec |

### 7.12. Sin tests

Escribe «sin tests» en el encargo, o pon `"tests": "none"` en las preferencias:

```
/feature Página de ayuda con el texto de docs/ayuda.md sin tests
```

- No se escriben tests nuevos ni se lanza `test-writer`.
- Los tests que ya existen en los componentes tocados se siguen pasando al cerrar. Es una
  comprobación que cuesta segundos y casi ningún token, y es la que avisa si has roto algo.
- El PR lo dice: «Sin tests nuevos, a petición».
- Si la tarea toca seguridad o un modelo real, el director te avisa una vez antes de seguir.
- En un `/fix`, el test que reproduce el fallo se escribe igualmente, salvo que lo excluyas.

## 8. Lo que el kit impide siempre

Los hooks lo bloquean y le explican a Claude por qué:

- `git commit`, `git merge` y `git push` estando en `main` o `master`.
- `git push` a `main`, con `--force` o con `--tags`.
- Crear o borrar etiquetas (`git tag v1.0.0`) y publicar releases (`gh release create`).
- `git reset --hard`.
- `git add -f` de `.claude/`, `CLAUDE.md` o `TASKS.md`.
- Escribir en cualquier carpeta `.github/` (el CI y el despliegue son de otro equipo).
- Escribir en componentes marcados `"readonly": true` en `project.json`.

- Escribir fuera de las carpetas del proyecto y de sus componentes, tanto con las herramientas
  de edición como con `>`, `cp`, `mv`, `tee` o `touch` hacia una ruta absoluta. Los ficheros
  temporales de los agentes van a `.claude/tmp/`.

Las ramas protegidas se cambian con `"protected_branches"` en `project.json`.

Límites:
- Los hooks vigilan lo que hace Claude Code, no lo que tecleas tú en la terminal. La protección
  de `main` en GitHub sigue siendo la barrera de verdad.
- La vigilancia de escrituras con comandos de consola es aproximada: no ve rutas relativas que
  salgan del proyecto ni lo que escriba un programa por dentro.
- **No abras Claude Code en una terminal de administrador.** Con permisos normales, un despiste
  de un agente fuera del proyecto falla; como administrador, escribe.

## 9. El tablero: `TASKS.md`

Desde la 0.4.0 el tablero es corto a propósito: una línea por tarea, una línea de historial por
tarea cerrada, y las hechas más antiguas archivadas en `.claude/TASKS-archivo.md`. El director lo
lee entero al empezar cada tarea, así que cada línea de más se paga siempre. Lo edita fila a
fila, nunca con sustituciones sobre el fichero: no está en git y no hay copia.

Si tu tablero viene de una versión anterior, pídele una vez: «Reduce TASKS.md al formato nuevo:
una línea por tarea, y archiva las hechas salvo las cinco últimas».

Una tabla con una fila por tarea y un historial de lo cerrado. Lo mantiene el director.

- **Siguiente acción:** una frase que otra sesión pueda ejecutar sin más contexto.
- **Estado:** pendiente · spec · aprobada · en curso · en revisión · hecha · bloqueada.
- Para verlo mientras trabajas, ábrelo en VS Code con la vista previa de Markdown
  (`Ctrl+Shift+V`): se refresca cuando el director lo edita. Los agentes en marcha se ven en
  Claude Code con `/tasks`.
- **Flujo · paso:** por ejemplo `feature · 7`. Es lo que usa `/resume`.

Puedes editarlo a mano o pedirle al director que cambie una tarea de estado o de prioridad.

`TASKS.md` no se versiona: solo existe en tu equipo. Si se pierde, el estado se reconstruye a
partir de las ramas, los PR y las specs.

## 10. Cambiar y actualizar el kit

El kit es la única fuente de los agentes y los comandos.

1. Edita el fichero en `idener-claude-kit\` (por ejemplo, `agents\reviewer.md`).
2. `python -m pytest` en el kit.
3. Apunta el cambio en `CHANGELOG.md` y sube `VERSION`.
4. Llévalo a cada proyecto:
   ```powershell
   python "$env:IDENER_KIT\install.py" <repo> --update --exclude-local
   ```
5. Cierra y abre `claude` en el proyecto.

Las reglas de trabajo viven en `.claude/kit-rules.md`, que es del kit y se actualiza solo.
`CLAUDE.md` es del proyecto y solo guarda lo suyo. Un `CLAUDE.md` instalado antes de la 0.1.3
lleva las reglas dentro: el instalador avisa y dice cómo migrarlo.

Si un proyecto necesita un agente propio, créalo en su `.claude/agents/` con otro nombre: las
actualizaciones no lo tocan.

**Cuándo añadir algo al kit:** cuando lo hayas hecho a mano dos veces y te haya costado. Mientras
tanto, apúntalo en `PROPUESTAS.md`.

## 11. Problemas comunes

| Síntoma | Causa y arreglo |
|---|---|
| No aparecen los comandos al escribir `/` ni los agentes con `@` | Has abierto `claude` fuera de la raíz del repo, o el kit se instaló con la sesión abierta. Cierra y abre `claude` desde la raíz |
| `claude agents` no lista los agentes | Ese comando abre otra cosa (sesiones en segundo plano). Usa `@` dentro de la sesión |
| Un hook da error en cada comando | `python` no está en el PATH, o la ruta del proyecto no se resuelve. Prueba `python .claude\scripts\guard_commands.py` a mano; si hace falta, cambia en `.claude/settings.json` la orden del hook por una ruta relativa: `python .claude/scripts/guard_commands.py` |
| El hook bloquea algo que debería pasar | Mira el motivo que da. Si es un fallo del guard, apúntalo en `PROPUESTAS.md` y corrígelo en el kit |
| `git status` enseña `CLAUDE.md` o `.claude/` | Faltan las exclusiones. Reinstala con `--update --exclude-local` |
| Tras `/clear`, `/resume` no sabe por dónde seguir | La columna «Flujo · paso» está vacía. Rellénala a mano y repite |
| Un agente toca ficheros que no le corresponden | Dile al director el ámbito exacto. Si se repite, endurece el fichero del agente en el kit |
| El director programa en vez de delegar | Recuérdaselo («delega en backend-dev»). Si se repite, refuerza la sección «Tu papel» de `CLAUDE.md` |
| Un hook bloquea una escritura «fuera del proyecto» que es legítima | Si es otro repo del proyecto, añádelo como componente en `project.json`. Si es un temporal, que vaya a `.claude/tmp/` |
| Aparece un fichero suelto en `C:\Program Files\Git\` | Un agente escribió en una ruta que empieza por `/` desde Git Bash. Bórralo, comprueba que no trabajas como administrador y actualiza el kit a la 0.1.3 o posterior |
| El push falla | No hay remoto o no tienes sesión en GitHub. El trabajo queda en la rama local |
| El director se para en cada cierre porque no hay remoto | Díselo una vez y pídele que lo anote en `CLAUDE.md` («Remoto y cierre de tareas») |
| Al abrir PowerShell sale un error del perfil «no está firmado digitalmente» | El equipo bloquea scripts sin firmar. Borra el perfil (`Remove-Item $PROFILE`) y usa la variable de entorno del §4 |
| Copias en conflicto o errores de git | OneDrive sincroniza mientras git escribe. Pausa la sincronización mientras trabajas |
| Ficheros con caracteres raros | Se crearon con `>` en PowerShell (UTF-16). Usa un editor o la opción `-o` de `a_markdown.py` |

## 12. Ampliaciones aplazadas

No están en el kit. Cada una se añade cuando aparezca su motivo; el diseño detallado de todas
está en la versión 0.7 de esta guía, que se conserva como archivo.

| Pieza | Se añade cuando |
|---|---|
| Agente `researcher` (webs y documentos largos) | Una feature dependa de leer webs largas |
| Agente `ui-tester` (pruebas en Chrome) | Se escape un fallo de interfaz que los tests no vieron |
| `/contract-change` y comprobación automática del contrato | Un cambio de API rompa el frontend |
| `/model-update` | Llegue la próxima entrega de un modelo |
| `/release` | Preparar las notas de versión a mano se haga pesado |
| `/new-project`, `/ga-backlog`, plantilla de variables v2 y su validador | Arranque un proyecto nuevo de verdad |
| Makefiles | Los comandos de compose de cada proyecto sean difíciles de recordar o de unificar |
| `/feature` que reparta un Grant Agreement en tareas | Arranquen proyectos nuevos a menudo |
| Tests dentro de los contenedores | El equipo deje de pasar los tests en local |
| Orden `idener`, ayuda y `doctor` | Lo use más gente del equipo |
| Tablero en GitHub Issues | `TASKS.md` se quede corto para coordinarse |
| Visor del tablero (página tipo kanban, solo lectura) | `TASKS.md` abierto al lado no baste para seguir el trabajo |

## 13. Historial

| Versión | Fecha | Cambios |
|---|---|---|
| 0.1–0.6 | 2026-10-04 | Diseño del kit completo (7 agentes, 16 comandos, 12 scripts) |
| 0.7 | 2026-10-05 | Revisión antes de construir: `researcher` sin Bash, «Flujo · paso», `ui-tester` opcional |
| 0.17 | 2026-10-06 | Kit 0.5.1, tras medir T17 y T33: las reglas de «sin flujo» pasan a las que se cargan siempre; el navegador siempre en un agente; el tablero se cierra en una edición; el director no toca los tests de aceptación; hábitos que ahorran (§7.9) |
| 0.16 | 2026-10-06 | Kit 0.5.0: preferencias por proyecto en `project.json`; modo sin tests; al cerrar solo se pasan los tests de los componentes tocados; reglas comunes reducidas a una página y el resto en `.claude/kit/`, que se lee bajo demanda; menos pasos del director; cambios triviales sin agente (§7.11, §7.12) |
| 0.15 | 2026-10-06 | Kit 0.4.0, tras medir una tarea mínima (0,98 $) y una de seguridad (16,85 $): en seguridad solo van con Opus la spec, la revisión y la lógica delicada; el director propone partir tareas grandes y avisa de que lo muy pequeño sale más barato sin flujo; tablero corto, con archivo y sin `sed`; `a_markdown.py` lee PDF |
| 0.14 | 2026-10-06 | Kit 0.3.0, tras medir tres tareas: el modelo de la sesión es lo que más pesa; tabla de modelos explícita (opus, sonnet, haiku) e independiente de la sesión; el director sugiere cambiar de modelo, no revisa diffs grandes ni prueba en el navegador por su cuenta; modelo anotado en tablero y PR; mediciones de referencia (§7.8) |
| 0.13 | 2026-10-06 | Kit 0.2.1: criterio de modo completo más estrecho. Replicar un patrón existente va en ligero aunque añada rutas, y un mock no cuenta como integrar un modelo |
| 0.12 | 2026-10-06 | Kit 0.2.0, para reducir el consumo: modo ligero por defecto y completo a petición; el director elige el modelo de cada encargo; specs de cinco a ocho criterios con los detalles como notas; tests solo de lo crítico; `smoke.py` para la conectividad; `/feature` acepta una spec ya escrita |
| 0.11 | 2026-10-05 | Tras probar el frontend en RENEUMA (kit 0.1.3): las reglas pasan a `.claude/kit-rules.md`, que se actualiza solo; los hooks bloquean escrituras fuera del proyecto; temporales en `.claude/tmp/`; `/adopt` avisa si falta compose; specs más proporcionadas; no trabajar como administrador |
| 0.10 | 2026-10-05 | Compose (kit 0.1.2): `/adopt` detecta compose y anota `run` en `project.json`; el cierre comprueba el contenedor cuando la tarea toca Dockerfile, compose, dependencias o un modelo (§7.4) |
| 0.9 | 2026-10-05 | Tras la prueba con RENEUMA (kit 0.1.1): variable de entorno en lugar del perfil de PowerShell; `/adopt` pregunta por el remoto; `/fix` reconoce lo que no es un defecto; la regla del mock aclara que varía con los inputs de forma artificial; responder a las preguntas no es aprobar la spec; cómo ver el tablero |
| 0.8 | 2026-10-05 | Versión reducida, junto con el kit 0.1.0 ya construido: 5 agentes, 4 comandos, 2 hooks. El cierre de tarea pasa a `CLAUDE.md`. El kit es la única fuente. Lo demás, aplazado (§12) |
