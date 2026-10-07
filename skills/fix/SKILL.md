---
name: fix
description: Corrige un defecto con un test que lo reproduce primero y el cambio mínimo después, hasta el PR preparado.
argument-hint: "<descripción del defecto, mensaje de error o log>"
disable-model-invocation: true
---
Defecto: "$ARGUMENTS".

Antes de nada, lee .claude/kit/director.md (modelos, tablero y cierre) y `preferences` de
.claude/project.json. El tablero se edita al registrar y al cerrar.

1. Clasifica: busca el comportamiento esperado en specs, contrato, documentos de referencia y
   tests existentes.
   - Si está escrito, es un fix: sigue.
   - Si lo que cambia es el comportamiento esperado: para y propón /feature.
   - Si no está escrito en ningún sitio: pregunta al usuario cuál es el correcto.
   - Si no hay ningún defecto que reproducir (limpieza, refactor, comentarios): dilo y propón
     hacerlo sin flujo.
2. Registra la tarea en TASKS.md (una línea) y crea la rama. Di con qué modelo corre la sesión;
   si es opus y el defecto no toca seguridad ni un modelo, sugiere `/model sonnet`.
3. Lanza el dev del componente, con el modelo que corresponda. El encargo, en este orden:
   escribir el test mínimo que reproduce el defecto, ejecutarlo y copiar en su respuesta la
   salida del fallo; después el cambio mínimo, sin refactorizar; después los tests en verde. Si
   no consigue reproducirlo, que pare y lo diga.
4. Comprueba que el test nuevo existe y que la salida del fallo corresponde al defecto. Revisa
   el diff: el cambio es mínimo y el test cubre el defecto. Lanza reviewer solo si el fix toca
   seguridad, la API o un modelo real, o si el diff es mayor de lo que el defecto justifica.
5. Cierra con "Cerrar una tarea" de .claude/kit/director.md.
