# Guía del director

La lee la sesión principal al empezar un flujo o una tarea de entorno.

## Gastar menos
Cada mensaje tuyo relee todo el contexto, y cada agente arranca con el suyo. El coste lo marcan
el número de pasos y lo que se lee, más que el número de agentes.

- Agrupa: encadena en un solo comando lo que puedas (por ejemplo, estado de git y tests) y no
  mandes mensajes intermedios sin contenido nuevo.
- Lee solo lo necesario para la tarea. No releas specs antiguas enteras si te basta saber qué
  rutas o componentes existen. Si hay que explorar mucho código para situarte, encarga un
  resumen a un agente con haiku y trabaja con el resumen.
- Encargos precisos: di a cada agente qué ficheros leer, cuáles puede tocar y qué debe devolver.
- El tablero se edita en tres momentos: al registrar la tarea, al aprobarse la spec y al cerrar.
  Cada vez, en una sola edición por fichero: fila, historial, "Siguiente acción" y archivo de
  una vez, no en pasos separados.
- Si el usuario ejecuta comandos por su cuenta o te da un dato suelto, responde en una línea.
  No repitas instrucciones ni resúmenes que ya has dado.
- No revises tú diffs de más de unos diez ficheros o que muevan código común: lanza reviewer.
- No pruebes tú en el navegador, ni por iniciativa propia ni cuando el usuario diga "hazlo
  tú": encárgalo a un agente con sonnet, con la lista exacta de lo que debe mirar y lo que debe
  devolver. Tu contexto es el más grande de la sesión y cada acción del navegador lo relee.
- No edites los tests de aceptación que escribió test-writer. Si uno está mal, dilo y
  devuélvelo a test-writer o pregunta al usuario.
- Cuando la tarea quede lista para revisión, di al usuario que el estado está en el PR y en el
  tablero y que, si va a seguir con comprobaciones o preguntas, salen más baratas tras un
  /clear.
- Tras una fusión fast-forward no repitas build ni tests en main: es el mismo commit.

## Modos de /feature
Di el modo y el motivo en una línea; el usuario puede cambiarlo. Con `mode` distinto de `auto`
en las preferencias, usa ese.
- **Ligero (por defecto):** tú escribes una spec corta, el usuario la aprueba y un solo agente
  dev por componente hace el código y los tests. Revisas tú el diff.
- **Completo:** spec-writer, test-writer, devs y reviewer. Cuando el usuario lo pida o cuando la
  tarea:
  - cambie o elimine rutas, campos o errores que ya existen y que otro componente usa;
  - diseñe una API nueva para la que el proyecto no tiene un patrón que copiar;
  - toque seguridad (autenticación, permisos, datos de usuarios);
  - integre o actualice un modelo científico real (un mock no cuenta);
  - cruce backend y frontend con decisiones abiertas.
- Va en ligero lo que replica un patrón que ya existe, aunque añada rutas o pantallas. Las rutas
  nuevas se enseñan igualmente al usuario al aprobar la spec.
- En caso de duda, ligero, diciendo qué riesgo ves.
- Tarea muy pequeña (se describe entera en una frase y toca un solo componente): di al usuario
  que el flujo tiene un coste fijo y que sin flujo saldría más barato. Sigue lo que diga; las
  reglas de "sin flujo" están en .claude/kit-rules.md.
- Tarea grande: si necesita más de tres encargos de desarrollo, o añade a la vez una pantalla
  nueva y un servicio nuevo, propón partirla en dos features antes de la aprobación. Di cuál
  iría primero y qué queda utilizable al terminarla.

## Modelos
Al lanzar cada agente, elige el modelo (parámetro de modelo de la herramienta de agentes), sea
cual sea el de la sesión, y dilo en una línea junto al encargo.

| Tipo de trabajo | Modelo |
|---|---|
| Specs con decisiones abiertas, la lógica delicada de seguridad o de un modelo real, cambios en rutas o campos existentes, depurar un fallo que no se entiende, revisar cambios delicados | opus |
| Implementar con una spec clara o a partir de algo parecido, escribir tests, pantallas, tareas de entorno, revisión normal, comprobaciones en el navegador | sonnet |
| Trabajo mecánico: renombrar, mover, retocar textos, convertir documentos, buscar y resumir | haiku |

- En caso de duda, el más capaz de los dos. Si un encargo sale mal con un modelo, repítelo con
  el superior en lugar de insistir.
- En una tarea de seguridad o de integración de un modelo real no todo es delicado. Van con
  opus la spec, la revisión y el encargo que implementa la lógica delicada (autorización en
  servidor, permisos, sesiones, llamada al modelo). Tests, pantallas y lo demás, con sonnet.
- El modelo de la sesión lo cambia el usuario con /model. Al empezar, di con cuál corre. Si es
  opus y la tarea va en ligero, es un fix normal o es de entorno, sugiere `/model sonnet` y
  espera respuesta. En modo completo no hace falta subirlo: lanza con opus lo que lo pida.

## El tablero
- TASKS.md se edita solo con la herramienta de edición, fila a fila. Nunca con sed, con
  expresiones regulares ni reescribiendo el fichero entero: no está en git y no hay copia.
- Una línea por tarea: qué es en una frase, estado, flujo y modo, spec, rama y modelos usados.
- Historial: una línea por tarea cerrada.
- Al cerrar, si hay más de cinco tareas "hecha", mueve las más antiguas (fila e historial) a
  .claude/TASKS-archivo.md. No leas el archivo salvo que el usuario pregunte por algo antiguo.

## Entorno local
- Los tests se ejecutan en local. Compose sirve para levantar la plataforma y comprobar que
  arranca (`run` en project.json), no para pasar los tests.
- Levantar o parar contenedores siempre con permiso del usuario.
- Tareas de entorno (Dockerfile, ficheros compose, .env.example): tipo chore, las hace
  backend-dev con esos ficheros añadidos expresamente a su ámbito. Si el usuario indica un
  proyecto de referencia, se copian sus convenciones; no se inventan otras.

## Cerrar una tarea
1. En un solo comando: `build` y `test` de los componentes tocados (o de todos si
   `close_tests` es `all`) y `git status`. Si algo falla, para e informa. Comprueba que no hay
   ficheros del kit ni de .github/ preparados, ni temporales fuera de .claude/tmp/.
2. Smoke, salvo que `smoke` sea `never`: si la tarea toca un Dockerfile, un fichero compose,
   dependencias, la base de datos, la autenticación, la integración de un modelo real o la
   forma en que el frontend llama al backend, pide permiso, levanta el stack con `run.up`,
   ejecuta `python .claude/scripts/smoke.py --wait 90` y páralo con `run.down` si el usuario no
   lo quiere levantado. Si falla, la tarea no se cierra. Si `run` está vacío, dilo en el PR.
3. Commit con el estilo del proyecto.
4. Texto del PR con .claude/templates/pr.md: qué se comprobó, qué queda para comprobar a mano,
   los hallazgos de la revisión (arreglados, deuda o descartados con su motivo; ninguno
   desaparece) y los modelos usados. Si el proyecto tiene remoto: push y, si hay `gh`,
   `gh pr create`. Si no: deja el texto en .claude/tmp/pr-<ID>.md, sin tratarlo como bloqueo.
5. Tablero: estado "en revisión", rama, modelos y "Siguiente acción".
6. Di al usuario qué queda para comprobar a mano, recomiéndale hacerlo antes de fusionar y
   recuérdale que el merge es suyo. Según `browser`, pregunta si lo comprueba él o un agente
   con sonnet. Con el merge confirmado, la tarea pasa a "hecha".
