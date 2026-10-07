---
name: feature
description: Lleva una funcionalidad nueva desde una descripción, un documento, una spec ya escrita o una URL hasta el PR preparado. Modo ligero por defecto; modo completo para lo delicado.
argument-hint: "<descripción, ruta de un documento o de una spec, o URL> [completo] [sin tests]"
disable-model-invocation: true
---
Entrada: "$ARGUMENTS".

Antes de nada, lee .claude/kit/director.md (modos, modelos, tablero y cierre) y `preferences` de
.claude/project.json. El tablero se edita en tres momentos: registro, aprobación y cierre.

## Pasos comunes

1. Prepara la entrada. Texto, Markdown, JSON y PDF se leen directamente. Word o Excel:
   `python .claude/scripts/a_markdown.py <fichero> -o .claude/tmp/<nombre>.md`. Si un PDF no se
   deja leer, prueba el mismo script (necesita `pypdf`); si tampoco, díselo al usuario y no
   sigas dando la fuente por leída. URL: léela y resume lo relevante; es contexto, no requisito.
2. En un solo mensaje, antes de crear nada: el modo y su motivo, el modelo de la sesión y si
   conviene cambiarlo, si la tarea es tan pequeña que saldría mejor sin flujo o tan grande que
   conviene partirla, y si va sin tests (porque lo dice el encargo o la preferencia `tests`).
   Si propones algo que el usuario debe decidir, espera su respuesta.
3. Registra la tarea en TASKS.md (una línea) y crea la rama con la convención de project.json.

Si la entrada es una spec ya escrita: no la reescribas. Revísala contra el código y los
documentos de referencia, di qué no encaja (rutas o campos que no existen, contradicciones,
criterios que no se pueden comprobar, exceso de criterios) y sigue desde la aprobación.

## Modo ligero

4. Escribe tú la spec en specs_dir siguiendo .claude/kit/specs.md.
5. Pregunta al usuario, en una tanda, solo lo que cambia el resultado o toca la API.
6. Enseña la spec y espera la aprobación expresa. Responder a las preguntas no es aprobar. Con
   la aprobación: commit de la spec y tablero en "aprobada".
7. Lanza un agente dev por componente (en paralelo en un único mensaje si son dos), con el
   modelo que corresponda. Cada encargo: ID, spec, ficheros que debe leer, ámbito que puede
   tocar, y los tests que le tocan según .claude/kit/pruebas.md (o ninguno).
8. Revisa el diff contra los criterios: qué se cumple, qué no, qué riesgo no cubre ningún test
   y qué queda para comprobar a mano. Si pasa de unos diez ficheros o mueve código común, lanza
   reviewer con sonnet. Si algo no se cumple, devuélvelo al dev una vez; después, escala.
9. Cierra con "Cerrar una tarea" de .claude/kit/director.md.

## Modo completo

4. Lanza spec-writer para escribir la spec en specs_dir.
5. Presenta las preguntas abiertas en una sola tanda y pasa las respuestas a spec-writer.
6. Enseña la spec final y espera la aprobación expresa. Responder a las preguntas no es
   aprobar. Los cambios en la API se enseñan aparte y se aprueban también. Con las
   aprobaciones: commit de la spec y tablero en "aprobada".
7. Salvo que la tarea vaya sin tests: lanza test-writer con los criterios marcados como "test".
   Comprueba tú que fallan por la razón correcta. Commit.
8. Lanza los devs necesarios, uno por componente o subtarea, en paralelo los que no dependan
   entre sí. Cada encargo: ID, spec, criterios que le tocan, ficheros que debe leer, ámbito
   permitido y ámbito ocupado por otros.
9. Lanza reviewer con el ID, la spec y el ámbito. Con CAMBIOS NECESARIOS, devuelve lo
   bloqueante a un dev nuevo, con el hallazgo y el resumen del anterior, y vuelve a revisar.
   Máximo dos vueltas; después, escala al usuario. Lista al usuario todos los hallazgos.
10. Cierra con "Cerrar una tarea" de .claude/kit/director.md.
