# Kit multiagente para Claude Code en Idener: resumen y veredicto

Oct 5, 2026 · @Alejandro Gomez

Actualizado el 7 de octubre de 2026, con el kit 0.5.1.

## Veredicto

El kit funciona, y desde la 0.3.0 su coste es razonable para tareas rutinarias: una funcionalidad pequeña sale por alrededor de un dólar a precio de lista, frente a los seis de la misma clase de tarea antes de ajustarlo.

- **Lo que hace bien.** Trabaja con disciplina: pregunta en vez de inventar, espera tu aprobación, prueba lo crítico y no se fía de los informes de sus propios agentes. Las barreras automáticas (hooks) funcionan en Windows.
- **Lo que se ha aprendido midiendo.** El número de agentes pesa poco en el coste. Pesa qué modelo lee y con cuánto contexto: el director, que relee todo en cada paso, era dos tercios del gasto cuando corría en Opus.
- **Lo que falta por ver.** Nunca se ha probado con un defecto real, y el primer uso en un proyecto real (REWET) acaba de empezar. RENEUMA es un banco de pruebas, no una validación.

La recomendación es trabajar con la sesión en Sonnet y dejar que el director lance con Opus solo lo delicado. Medido en dos tareas de seguridad: con todos los agentes en Opus, 17 dólares; con Opus solo en la spec, la lógica del servidor y la revisión, 6 dólares en una tarea cuatro veces más pequeña y con la misma calidad. Lo que queda por reducir es el número de pasos del director.

## Qué es y qué trae

`idener-claude-kit` es un conjunto pequeño de ficheros que se copian en un repo para que Claude Code trabaje siempre igual: una spec corta que tú apruebas, el código con los tests de lo crítico, una revisión y un PR preparado que tú fusionas. Todo lo que instala queda fuera de git. La versión actual es la 0.5.1.

| Pieza | Tipo | Para qué |
| --- | --- | --- |
| `spec-writer` | Agente | Escribe la spec en el modo completo |
| `test-writer` | Agente | Escribe los tests críticos antes que el código, en el modo completo |
| `backend-dev` | Agente | Implementa en el backend (FastAPI), con sus tests en modo ligero, y hace las tareas de entorno |
| `frontend-dev` | Agente | Implementa en el frontend (Blazor), con sus tests en modo ligero |
| `reviewer` | Agente | Compara los cambios con la spec en el modo completo; no modifica nada |
| `/adopt` | Comando | Deduce cómo es el proyecto, una vez |
| `/feature` | Comando | Funcionalidad nueva, de la idea al PR. Modo ligero por defecto y completo a petición |
| `/fix` | Comando | Defecto: test que lo reproduce y cambio mínimo, con un solo agente |
| `/resume` | Comando | Retoma el trabajo tras limpiar el contexto |
| `guard_commands.py` | Hook | Impide commits en `main`, etiquetas, releases, push forzado y escrituras fuera del proyecto |
| `guard_paths.py` | Hook | Impide editar `.github/`, componentes de solo lectura y rutas fuera del proyecto |
| `a_markdown.py` | Script | Pasa Excel, Word y PDF a Markdown para que lo lean los agentes |
| `smoke.py` | Script | Comprueba la conectividad entre frontend, backend y base de datos con el stack levantado |
| `install.py` | Instalador | Instala y actualiza el kit en un repo |

En cada proyecto quedan estos ficheros de trabajo: `.claude/kit-rules.md` (reglas comunes del kit, una página, se cargan siempre), `.claude/kit/` (guía del director, qué se prueba y cómo se escribe una spec; se leen solo cuando hacen falta), `CLAUDE.md` (lo propio del proyecto), `TASKS.md` (el tablero), `.claude/project.json` (componentes, comandos, entorno y preferencias) y `.claude/settings.json` (permisos y hooks).

## Cómo hemos llegado hasta aquí

El diseño empezó grande, se recortó antes de construirse y se ha ido corrigiendo con lo que salió al usarlo.

| Etapa | Qué se hizo | Qué se aprendió |
| --- | --- | --- |
| Propuesta inicial | Un director, un agente de documentación, agentes de backend y frontend y un cuadro de mandos | El director es la propia sesión de Claude Code; el contexto se gestiona con tareas pequeñas y estado en ficheros, no vigilando |
| Guía 0.1 a 0.7 | Diseño completo sobre el papel: 7 agentes, 16 comandos, 12 scripts, Makefiles, ayuda | Demasiado para algo que no había hecho ni una tarea real |
| Reducción | Recorte a 5 agentes, 4 comandos y 2 hooks, y construcción directa del kit (0.1.0) | Costaba lo mismo escribir las piezas que describirlas |
| Prueba con RENEUMA | Proyecto ficticio de reciclaje de neumáticos, con un Grant Agreement y dos plantillas con errores puestos a propósito | El flujo funciona y encuentra las trampas |
| 0.1.1 | Aprobación expresa de la spec, pregunta por el remoto, regla del mock, `/fix` sin defecto | Las reglas ambiguas generan preguntas repetidas |
| 0.1.2 | Compose: `/adopt` lo detecta y el cierre comprueba el contenedor | El recorte había dejado fuera algo que todos los proyectos reales usan |
| 0.1.3 | Reglas en un fichero del kit que se actualiza solo, bloqueo de escrituras fuera del proyecto, specs más proporcionadas | Un agente escribió un fichero en `C:\Program Files\Git\`; las reglas dentro de `CLAUDE.md` no se actualizaban |
| 0.2.0 | Modo ligero por defecto, modelo según la tarea, specs de cinco a ocho criterios, tests solo de lo crítico, `smoke.py`, specs escritas fuera | El flujo completo estaba dimensionado para lo delicado y se usaba para todo: dos sesiones completas en tres tareas pequeñas |

Después vinieron cuatro ajustes derivados de medir:

| Versión | Qué cambió | Qué lo motivó |
| --- | --- | --- |
| 0.2.1 | Criterio del modo completo más estrecho | El director lo elegía para cualquier tarea que añadiera rutas |
| 0.3.0 | Tabla de modelos explícita, aviso del modelo de la sesión, revisor para diffs grandes, navegador solo a petición | El director en Opus era dos tercios del gasto |
| 0.4.0 | En seguridad, Opus solo para la spec, la revisión y la lógica delicada; partir tareas grandes; tablero corto con archivo | Una tarea de seguridad costó 17 dólares con todos los agentes en Opus |
| 0.5.0 | Reglas comunes en una página y el resto bajo demanda; menos pasos del director; preferencias por proyecto; modo sin tests | El contexto de arranque son 41.000 tokens que se releen en cada paso |

## Qué está probado y qué no

Los dos modos de `/feature`, la elección de modelo, `smoke.py` y las reglas de la 0.3.0 están comprobados en RENEUMA. Las de la 0.4.0 y la 0.5.0 se vieron en T17 y T33. Siguen sin probar las reglas de la 0.5.1, `/fix` con un defecto real y un proyecto con varios repos.

| Qué | Estado | Dónde se vio |
| --- | --- | --- |
| Instalador, hooks, conversor y smoke (76 tests) | Probado en Linux | Tests del kit |
| Instalación en Windows, rutas con espacios y OneDrive | Comprobado | RENEUMA |
| Carga de agentes y comandos, bloqueo de `git tag` | Comprobado | RENEUMA |
| `/adopt` | Comprobado | RENEUMA |
| `/feature` completo de backend | Comprobado | T8: mock de pirólisis |
| `/feature` completo de frontend con tests bUnit | Comprobado | T10: página de simulación |
| `/resume` tras `/clear` | Comprobado | T8 |
| `/feature` en modo ligero | Comprobado | T29 y T30 |
| Elección de modelo por encargo | Comprobado | T28 a T30; `/usage` desglosa el consumo por modelo |
| `/feature` con una spec escrita fuera | Sin probar | Primera spec externa |
| `/fix` con un defecto real | Sin probar | T9 fue una limpieza, no un defecto |
| `smoke.py` y comprobación del contenedor al cerrar | Comprobado | T28 y T29 |
| Bloqueo de escrituras fuera del proyecto en Windows | Sin probar | Paso 2.9 del plan |
| Importación de `kit-rules.md` desde `CLAUDE.md` | Comprobado | `/context` lo muestra cargado como fichero de memoria |
| Proyecto con varios repos (`--role secondary`) | Sin probar | Piloto real |
| Un proyecto real | En curso | REWET, desde octubre de 2026 |

## Lo que funcionó y lo que falló en la prueba

### Funcionó

- **Encontró las trampas.** Detectó el valor por defecto fuera de rango, el input sin valor por defecto y el gráfico sin eje X, y redactó las preguntas para el equipo de modelado sin enviarlas.
- **Encontró algo que no era trampa.** El modelo pedía Python 3.11 y el equipo tenía 3.10.
- **Preguntó en vez de decidir.** Las preguntas llegaron agrupadas, con una propuesta cada una, y los cambios de API separados para aprobación expresa.
- **Comprobó por su cuenta.** El director pasó él los tests, miró qué ficheros se habían tocado y avisó cuando un agente hizo algo no pedido.
- **Fue honesto.** Etiquetó como `refactor` lo que no era un fix y dijo qué criterios quedaban sin probar a mano.
- **Retomó bien.** Tras `/clear`, `/resume` localizó la tarea y el paso, y verificó el repo antes de seguir.

### Falló o molestó

| Problema | Qué se hizo |
| --- | --- |
| El perfil de PowerShell está bloqueado en el equipo | La ruta del kit va en una variable de entorno de Windows |
| El director se paraba en cada cierre por no haber remoto | `/adopt` lo pregunta y lo deja anotado |
| Dos reglas del mock chocaban y generaban una pregunta | Regla aclarada: varía con los inputs de forma artificial y declarada |
| Limpieza tratada como `/fix`, con cuatro agentes | `/fix` reconoce lo que no es un defecto |
| Spec de 31 criterios para una página, y cuatro preguntas más tras aprobarla | Regla de proporción en `spec-writer` y detalles de pantalla cerrados antes |
| Un agente escribió un fichero en `C:\Program Files\Git\` | Hooks que bloquean escrituras fuera del proyecto; temporales solo en `.claude/tmp/` |
| Las reglas no se actualizaban con el kit | Reglas en `.claude/kit-rules.md`, del kit |
| El recorte dejó fuera compose | Recuperado en la 0.1.2 |
| Consumo muy alto | Medido y reducido. Ver la sección siguiente |

## El coste en tokens

Era el problema abierto más importante: las tres primeras tareas consumieron dos sesiones completas. Ya está medido y, para lo rutinario, resuelto.

Antes de medir, el gasto se atribuía a cinco causas. Las mediciones confirmaron casi todas y corrigieron la primera: el número de agentes resultó pesar poco frente a qué modelo lee y cuántos pasos se dan.

- **Muchos agentes por tarea.** Un `/feature` lanza cuatro o cinco, y cada uno lee el proyecto, la spec y las reglas desde cero.
- **Specs grandes.** 31 criterios generan 45 tests que hay que escribir, ejecutar y revisar.
- **El modelo más caro en todo.** Los agentes heredan el modelo de la sesión, así que retocar un comentario cuesta como diseñar una spec.
- **Flujo completo para cosas pequeñas.** Una limpieza usó cuatro agentes.
- **Sesiones largas.** Cada turno relee la conversación acumulada.

### Mediciones

Tomadas en RENEUMA el 6 de octubre de 2026 con `/usage`, a precio de lista. Son siete tareas distintas, no la misma repetida, así que dan el orden de magnitud y no una comparación exacta.

| Tarea | Modo | Director | Coste | Tiempo de API | Tamaño |
| --- | --- | --- | --- | --- | --- |
| T28: backend simulado de desvulcanización | Completo | Opus | Más de 2,04 $ (medido a mitad de tarea) | Más de 6 min | 3 rutas, 15 tests nuevos |
| T29: página de desvulcanización, unificando código con pirólisis | Ligero | Opus | 6,01 $, de los que 4,02 fueron del director | 10 min 39 s | 43 ficheros, 920 líneas, 4 tests nuevos, prueba en navegador |
| T30: descarga de resultados en CSV | Ligero | Sonnet | 1,16 $ | 4 min | 11 ficheros, 257 líneas, 4 tests nuevos |
| T31: botón para restablecer valores por defecto | Ligero | Sonnet | 0,98 $ | 2 min 16 s | 7 ficheros, 192 líneas, 4 tests nuevos |
| T32: roles y página de administración de usuarios | Completo | Sonnet, con todos los agentes en Opus | 16,85 $, de los que 14,99 fueron de los agentes | 45 min 38 s | 42 ficheros, 2.405 líneas, 30 tests nuevos, smoke |
| T17: proteger el backend con una clave | Completo | Sonnet, con Opus solo en spec, backend y revisión | 6,37 $, de los que 2,27 fueron en Opus | 16 min 59 s | 18 ficheros, 623 líneas, smoke y tres rondas en el navegador |
| T33: cambiar el texto de un botón | Sin flujo | Sonnet, sin agentes | 0,48 $ | 1 min 12 s | 2 ficheros, y después la documentación |

Lo que dicen:

- **El modo ligero con el director en Opus fue lo más caro.** Al quitar agentes, la spec y la revisión pasaron al modelo más caro y con más contexto. El director releyó 6,6 millones de tokens en 52 peticiones.
- **La prueba en el navegador hecha por el director es lo más caro de una sesión.** Unas veinte acciones, cada una releyendo todo el contexto.
- **Con el director en Sonnet la calidad se mantuvo** en una tarea rutinaria: spec de seis criterios, decisiones señaladas, pregunta ante un test que chocaba y comprobaciones hechas por él. Su revisión del diff fue más escueta que la de Opus.
- **La elección de modelo por encargo funciona.** `/usage` muestra el consumo por modelo y confirma que los agentes corrieron en el modelo pedido.
- **La barra de uso del plan no sirve para comparar tareas.** Es compartida con el resto de lo que se haga con Claude en ese periodo.

Lo que añadieron T31 y T32:

- **Un `/feature` tiene un coste fijo de alrededor de un dólar.** T31 era más pequeña que T30 y costó casi lo mismo. Lo muy pequeño sale más barato sin flujo.
- **El director en Sonnet aguanta una tarea compleja.** En T32 orquestó ocho encargos durante una hora y veinte por 1,86 $, sin perder el hilo ni saltarse comprobaciones.
- **La calidad en seguridad fue alta.** El revisor encontró una condición de carrera que podía dejar la plataforma sin administrador y un fallo de arranque que venía de una decisión del propio director, que lo reconoció.
- **Casi todo el gasto de T32 fue de agentes en Opus haciendo también tests y pantallas.** La regla decía «no bajes de Opus en nada que toque seguridad» y el director la aplicó a los ocho encargos. Los tests se llevaron casi la mitad del tiempo de agente.
- **El número de criterios no mide el tamaño.** T32 tenía ocho criterios y 2.405 líneas. Debió partirse en dos.
- **T32 consumió media ventana de sesión del plan.** Con el esquema actual caben dos tareas así por ventana.

La 0.4.0 responde a esto: en seguridad solo van con Opus la spec, la revisión y la lógica delicada; el director propone partir las tareas grandes y avisa de que lo muy pequeño sale más barato sin flujo; y el tablero pasa a una línea por tarea, con archivo.

### De dónde sale el coste fijo

`/context`, justo después de un `/clear`, mostró 41.000 tokens ocupados antes de escribir nada:

| Qué | Tokens | De quién depende |
| --- | --- | --- |
| Herramientas de Claude Code | 20.300 | De Claude Code |
| Reglas del kit (`kit-rules.md`) | 4.200 | Del kit |
| Skills sincronizadas e integradas | 4.800 | De Claude Code y de la cuenta |
| Mensajes de arranque | 4.700 | De Claude Code |
| Prompt del sistema | 4.200 | De Claude Code |
| `CLAUDE.md` del proyecto | 1.400 | Del proyecto |
| Agentes, MCP y memoria | 1.700 | Mixto |

Cada paso del director y cada llamada de cada agente relee al menos esa base, y el kit solo controla una parte pequeña de ella. Un `/feature` mínimo son unas cuarenta o cincuenta relecturas, y de ahí sale el dólar. La conclusión es que recortar reglas ayuda poco y reducir pasos ayuda mucho.

La 0.5.0 hace las dos cosas: deja en una página las reglas que se cargan siempre, con el resto en ficheros que se leen bajo demanda, y reduce los pasos del director (tablero en tres momentos, comandos agrupados, cambios triviales sin lanzar un agente). También añade preferencias por proyecto en `project.json` y el modo sin tests.

Medido tras instalarla: las reglas del kit bajaron de 4.200 a 1.300 tokens y el arranque de 41.300 a 36.700. El kit ocupa ahora menos del 5 % de la base; el resto es de Claude Code. Lo que queda por ganar está en el número de pasos, no en el tamaño de las reglas.

### Lo que añadieron T17 y T33, con la 0.5.0

- **El reparto de modelos funciona.** En T17 el director anunció qué agente iba con qué modelo antes de empezar, y Opus fue un tercio del coste, frente a casi todo en T32.
- **El gasto se movió al director.** Hizo 73 peticiones, casi el triple que en T32, por tres rondas de pruebas en el navegador hechas por él mismo, las preguntas en la misma sesión y un cierre del tablero en ocho ediciones.
- **Cada mensaje en una sesión cargada cuesta entre dos y cinco céntimos, diga lo que diga.** T33 fueron 20 mensajes para un cambio de dos líneas: el cambio costó poco y la conversación, el resto.
- **Sin flujo, el director no leyó su guía.** Editó estando en `main` y no pasó los tests. Era el riesgo previsto de la 0.5.0, y apareció en el camino que no pasa por un comando.
- **La calidad en seguridad se mantuvo con Sonnet en los tests y el frontend.** El revisor probó unas veinte formas de saltarse el 401 y encontró dos fallos reales.

La 0.5.1 responde a esto: las reglas de «sin flujo» pasan a las que se cargan siempre, las pruebas en el navegador van siempre a un agente, el tablero se cierra en una sola edición y el director no toca los tests de aceptación. Y hay tres hábitos tuyos que ahorran más que cualquier regla: lanzar los comandos de git en otra terminal, hacer `/clear` cuando la tarea quede lista para revisión y juntar en un mensaje lo que vayas a pedir.

### Lo que hace el kit para reducirlo

| Cambio | Desde | Qué se pierde |
| --- | --- | --- |
| Modo ligero por defecto y completo solo en lo delicado | 0.2.0 | Tests escritos por quien implementa y revisión del director |
| Specs de cinco a ocho criterios y tests solo de lo crítico | 0.2.0 | Lo que no tiene test puede romperse sin avisar |
| `smoke.py` para la conectividad | 0.2.0 | Necesita el stack levantado |
| Criterio de modo completo más estrecho: replicar un patrón va en ligero | 0.2.1 | Hay que mirar qué modo elige el director |
| El director avisa si la sesión corre en Opus para algo rutinario | 0.3.0 | Depende de que cambies el modelo con `/model` |
| El director no revisa diffs de más de unos diez ficheros: lanza `reviewer` con Sonnet | 0.3.0 | Un agente más en tareas grandes |
| El director no prueba en el navegador por su cuenta: pregunta y, si se quiere, lo delega | 0.3.0 | La comprobación visual vuelve a ser tuya por defecto |
| En seguridad, Opus solo para la spec, la revisión y la lógica delicada | 0.4.0 | Tests y pantallas de una tarea de seguridad los hace Sonnet |
| El director propone partir las tareas grandes y avisa de que lo mínimo sale más barato sin flujo | 0.4.0 | Una decisión más al empezar |
| Tablero de una línea por tarea, con archivo de las hechas | 0.4.0 | El detalle hay que buscarlo en la spec y en el PR |
| Reglas comunes en una página; lo demás se lee bajo demanda | 0.5.0 | El director tiene que acordarse de leer su guía |
| Menos pasos: tablero en tres momentos, comandos agrupados, encargos con lista de ficheros | 0.5.0 | El tablero ya no dice en qué paso exacto va la tarea |
| Cambios triviales sin flujo hechos por el director, sin lanzar un agente | 0.5.0 | Sin spec, sin revisión y con los tests que ya existan |
| Al cerrar, solo los tests de los componentes tocados | 0.5.0 | Un fallo cruzado entre componentes lo vería el smoke, no los tests |
| Modo sin tests a petición | 0.5.0 | La funcionalidad nueva queda sin red propia |

## Recomendaciones de uso

### Qué modo usar

La regla práctica: si puedes describir el resultado en un párrafo y sabes comprobarlo a ojo, pídelo directo; si al escribir el encargo te salen dudas, usa `/feature`.

| Tipo de trabajo | Cómo pedirlo |
| --- | --- |
| Preguntas, exploración, entender código | Al chat, sin comando |
| Textos, estilos, retoques, limpiezas | Al chat, sin comando |
| Una pantalla o un endpoint parecido a otro que ya existe | Al chat, encargándolo a un solo agente dev |
| Entorno: Dockerfile, compose, `.env.example` | Al chat, como tarea de entorno |
| Funcionalidad con decisiones abiertas | `/feature` (modo ligero) |
| Cambios en la API | `/feature … completo` |
| Seguridad: autenticación, permisos, datos de usuarios | `/feature … completo` |
| Un fallo con comportamiento esperado conocido | `/fix` |

Para encargar algo directo sin que el director monte el flujo, díselo: «Sin flujo y sin spec: encárgale solo a frontend-dev…».

### Qué modelo usa cada encargo

Hay dos modelos en juego. El de la sesión, que es el del director, lo eliges tú con `/model` y es lo que más pesa en el coste: para lo rutinario, Sonnet. El de cada agente lo elige el director en cada encargo con esta tabla, sea cual sea el modelo de la sesión, y te lo dice.

| Tipo de trabajo | Modelo |
| --- | --- |
| Specs con decisiones abiertas, la lógica delicada de seguridad o de un modelo real, cambios en rutas o campos existentes, fallos difíciles, revisiones delicadas | `opus` |
| Implementar con spec clara o a partir de algo parecido, tests, pantallas, entorno, revisión normal, comprobaciones en el navegador | `sonnet` |
| Trabajo mecánico: renombrar, textos, convertir documentos, buscar | `haiku` |

- Si un encargo sale mal con un modelo, se repite con el superior.
- En una tarea de seguridad no todo va con Opus: la spec, la revisión y el encargo con la lógica delicada sí; los tests, las pantallas y el resto, con Sonnet.
- En modo completo no hace falta subir la sesión a Opus: el director lanza con Opus los encargos que lo piden, aunque él corra en Sonnet. Puedes imponer otro modelo en cualquier momento.
- El modelo de cada encargo queda anotado en el tablero y en el PR. El dato real lo da `/usage`, que desglosa el consumo de la sesión por modelo. El contador se reinicia con `/clear`: para medir una tarea, limpia antes de empezar y mira `/usage` al terminar.

### Qué se prueba

Se prueba lo crítico, no todo. Un test por criterio ya no es la regla.

| Qué | Tests automáticos |
| --- | --- |
| Cada ruta del backend | Caso normal, un error de validación con su campo y forma de la respuesta |
| Integración de un modelo | Unidades, valores por defecto y aislamiento entre dos peticiones seguidas |
| Seguridad | Sin sesión se rechaza; con un rol que no corresponde se rechaza |
| Cada pantalla | Dos o tres como mucho, de lo que es fácil que falle |
| Un fix | El test que reproduce el defecto |

- No se escriben tests de etiquetas, textos, atributos ni menús: van a la lista «Comprobar a mano» del PR.
- La conectividad se comprueba con el stack levantado y `python .claude\scripts\smoke.py`, que lee de `project.json` (`run.health`) qué debe responder: URLs, puertos como `tcp://localhost:5432` y, si quieres, una llamada completa de extremo a extremo.
- El director lo ejecuta al cerrar las tareas que tocan contenedores, dependencias, base de datos, autenticación, modelos o la comunicación entre frontend y backend.

### Cómo son las specs

- De cinco a ocho criterios de aceptación. Con más de diez, se parte la tarea.
- Un criterio es un comportamiento que te importaría que fallara, y dice cómo se comprueba: test, smoke o manual.
- Los detalles (tipos de control, textos, orden de campos) van en «Notas de implementación» y no generan tests.
- Solo te pregunta lo que cambia el resultado o toca la API; lo demás lo decide y lo deja anotado.
- Cabe en una pantalla, para que la leas entera antes de aprobar.

### Preferencias del proyecto

Cuánto se hace de cada cosa se ajusta por proyecto en `preferences` de `.claude/project.json`, sin tocar el kit. Si falta una clave vale el primer valor, y lo que escribas en el encargo manda sobre la preferencia para esa tarea.

| Clave | Valores |
| --- | --- |
| `tests` | `critical`: lo crítico · `none`: no se escriben tests nuevos · `full`: un test por criterio |
| `close_tests` | `touched`: al cerrar, solo los tests de los componentes tocados · `all`: los de todos |
| `mode` | `auto`: el director elige · `light` · `full` |
| `smoke` | `ask`: pide permiso cuando toca · `never` |
| `browser` | `ask`: pregunta al cerrar · `user`: siempre tú · `agent`: siempre un agente |
| `max_criteria` | `8`: tope de criterios por spec |

### Sin tests

Escribe «sin tests» en el encargo, o pon `"tests": "none"` en las preferencias.

- No se escriben tests nuevos ni se lanza `test-writer`, y el PR lo dice.
- Los tests que ya existen en los componentes tocados se siguen pasando al cerrar. Cuesta segundos y casi ningún token, y es lo que avisa si se ha roto algo.
- Si la tarea toca seguridad o un modelo real, el director avisa una vez antes de seguir.
- En un `/fix`, el test que reproduce el fallo se escribe igualmente, salvo que lo excluyas.

### Tareas mínimas

Un `/feature` tiene un coste fijo de alrededor de un dólar. Para un texto, un estilo o un botón sencillo, pídelo «sin flujo»: desde la 0.5.0 el director lo hace él directamente en una rama, sin lanzar un agente, y pasa los tests del componente.

### Hábitos

- **Lee la spec antes de aprobar.** Es lo que se va a construir. Si tiene criterios que no te importan, pide que los quite.
- **`/clear` entre tareas, siempre.** Y `/resume` si había algo a medias.
- **Trabaja con la sesión en Sonnet para lo rutinario.** Se cambia con `/model` y queda guardado como modelo por defecto.
- **No abras Claude Code como administrador.** Con permisos normales, un despiste fuera del proyecto falla en vez de escribir.
- **El merge es tuyo.** Mira el diff y prueba a mano lo que el director te indique antes de fusionar.
- **Ten `TASKS.md` abierto al lado**, con la vista previa de Markdown de VS Code. `/tasks` enseña los agentes en marcha.
- **Para copiar un estilo**, da rutas concretas de otro proyecto o una captura de pantalla, no solo una URL.
- **Apunta lo que moleste** en `PROPUESTAS.md` del kit mientras trabajas.

### Cuándo cambiar el kit

- Algo entra cuando se ha hecho a mano dos veces y ha costado.
- Algo sale cuando no ha evitado ningún problema en cinco tareas.
- Cada cambio: editar el kit, `python -m pytest`, anotar en `CHANGELOG.md`, subir `VERSION` y actualizar los proyectos con `--update`.

### Specs escritas fuera, con otro LLM

Es compatible: para el kit una spec es un fichero Markdown en `docs/specs/`, sea quien sea su autor. Ahorra consumo, porque leer un PDF largo y redactar la spec es de lo más caro del flujo.

1. **Dale al otro LLM la plantilla del kit** (`.claude/templates/spec.md`) y pídele ese formato: de cinco a ocho criterios de aceptación numerados (CA-01…) y verificables, cada uno con su forma de comprobación (test, smoke o manual), sección «Impacto en la API», los detalles en «Notas de implementación» y las dudas en «Preguntas abiertas» sin inventar la respuesta.
2. **Guarda el resultado** en el repo, por ejemplo `docs/specs/T14-nombre.md`.
3. **Lánzala con `/feature`:** `/feature docs/specs/T14-nombre.md`. Desde la 0.2.0, el comando reconoce una spec ya escrita: no la reescribe, la revisa contra el código y los documentos de referencia, te dice qué no encaja (rutas o campos que no existen, contradicciones, criterios que no se pueden comprobar, exceso de criterios) y espera tu aprobación.
4. **En modo barato**, sin flujo: «Sin flujo: encárgale a backend-dev implementar docs/specs/T14-nombre.md, con sus tests».

Dos advertencias:

- **Confidencialidad del Grant Agreement.** Suele ser un documento restringido del consorcio. Antes de subirlo a otro servicio, comprueba que el proyecto y la empresa lo permiten y qué hace ese servicio con lo que recibe.
- **Las specs externas tienden a ser largas.** Pide pocos criterios y concretos, y recorta antes de aprobar: cada criterio de más son tests y revisión que se pagan después.

## Próximos pasos

Por este orden. Los primeros cierran lo que queda por comprobar en RENEUMA; los dos últimos antes de las ampliaciones son ya uso real.

1. **Reducir el tablero al formato nuevo** y añadir el bloque `preferences` a `project.json`. La 0.5.0 ya está instalada y `/context` confirma que las reglas han bajado.
2. **Instalar la 0.5.1 y repetir un cambio mínimo sin flujo**, para comprobar que ahora crea la rama antes de tocar nada y pasa los tests.
3. **`/fix` con un defecto real.** Es el único comando que no se ha probado como fue diseñado, con el test que falla primero.
4. **Comprobar a mano lo que se fusionó sin probar:** la descarga en CSV, el botón de reset y los roles con la página de administración. Las listas están en los textos de PR de cada tarea.
5. **Piloto real (en curso en REWET):** instalar en un proyecto existente, `/adopt` y un `/fix` con un fallo de verdad. Es la primera prueba del test que falla primero.
6. **Primera `/feature` real** y comparación honesta con lo que habría costado pedirla al chat: tiempo tuyo, calidad y sorpresas. De ahí sale cuánto seguir invirtiendo.
7. **Ampliaciones**, solo si el uso las pide: agente para probar la interfaz en el navegador, visor del tablero, comando de releases, proyecto nuevo desde el Grant Agreement. El diseño de todas está en la guía 0.7, guardada como archivo.

## Riesgos y límites

- **Los hooks son un cinturón, no un muro.** Vigilan lo que hace Claude Code, no lo que tecleas tú. No ven rutas relativas que salgan del proyecto ni lo que escriba un programa por dentro. La protección de `main` en GitHub sigue siendo la barrera de verdad.
- **El tablero solo existe en tu equipo.** `TASKS.md` no se versiona. Si se pierde, el estado se reconstruye desde las ramas, los PR y las specs.
- **OneDrive y git conviven mal.** Si aparecen copias en conflicto o errores de git, pausa la sincronización mientras trabajas.
- **La disciplina no sustituye al criterio.** Si la spec aprobada está mal, todo lo demás saldrá mal con mucha precisión. El punto de control eres tú.
- **Los tests no ven lo visual.** Que una página quede bien se comprueba a ojo.
- **El modo directo tiene menos red.** Sin spec ni revisión independiente, los problemas aparecen al probar, no antes.
- **Está hecho para una persona.** Si lo usa más gente del equipo, cada uno tendrá su tablero y harán falta la ayuda y un tablero compartido que se dejaron aplazados.
- **Depende de Claude Code.** Los comandos, los agentes y los hooks usan funciones que cambian entre versiones. Tras una actualización grande conviene repetir las comprobaciones básicas.

* **El modo ligero tiene menos red que el completo.** Quien implementa escribe sus tests y la revisión la hace el director, no un agente independiente. Si el director elige ligero para algo delicado, cámbialo a completo.
* **Probar menos tiene un coste.** Lo que no tiene test puede romperse sin avisar cuando alguien toque ese código más adelante. Con las rutas cubiertas, el riesgo queda en la interfaz.

- **La 0.5.0 depende de que el director lea su guía.** Los modos, los modelos y los pasos de cierre ya no se cargan solos: los comandos le dicen que lea `.claude/kit/director.md` al empezar. Si en una tarea no anuncia modo ni modelo, es que no la ha leído.
- **Sin tests y sin flujo son atajos.** Sirven para lo pequeño y lo que se comprueba a ojo. Usados por sistema en lo que importa, devuelven el problema que el kit quería evitar.

## Referencia rápida

| Quiero | Hago |
| --- | --- |
| Instalar el kit en un repo | `python "$env:IDENER_KIT\install.py" <repo> --exclude-local` |
| Instalar en el segundo repo de un proyecto | Lo mismo, con `--role secondary` |
| Actualizar un repo tras cambiar el kit | Lo mismo, con `--update` |
| Ver qué haría sin tocar nada | Lo mismo, con `--dry-run` |
| Comprobar el kit | `python -m pytest` en la carpeta del kit |
| Preparar el proyecto, una vez | `/adopt` |
| Funcionalidad nueva | `/feature <descripción, fichero o URL>` (modo ligero) |
| Funcionalidad delicada: API, seguridad, modelos | `/feature <...> completo` |
| Funcionalidad sin tests nuevos | `/feature <...> sin tests` |
| Usar una spec escrita fuera | `/feature docs/specs/<fichero>.md` |
| Cambio mínimo | «Sin flujo: …» |
| Arreglar un fallo | `/fix <descripción>` |
| Cambiar cuánto se prueba, el modo o el smoke en un proyecto | `preferences` en `.claude/project.json` |
| Comprobar la conectividad | Con el stack levantado: `python .claude\scripts\smoke.py` |
| Retomar | `/clear` y `/resume` |
| Medir el consumo de una tarea | `/clear` antes y `/usage` al terminar |
| Ver qué ocupa el contexto | `/context` |
| Ver agentes en marcha y su modelo | `/tasks` |
| Cambiar el modelo de la sesión | `/model` |
| Desinstalar | Borrar `.claude/`, `CLAUDE.md` y `TASKS.md` |

Documentos que acompañan a este resumen: `guia-multiagente-idener.md` (cómo se usa cada pieza), `plan-puesta-en-marcha.md` (pasos de prueba y piloto) y `CHANGELOG.md` del kit (qué cambió en cada versión).

Los apuntes para la siguiente versión del kit están en `kit-pendientes.md`, en el proyecto «Trabajo».
