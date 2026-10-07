---
name: resume
description: Retoma el trabajo en una sesión limpia a partir del tablero y del estado de git.
disable-model-invocation: true
---
1. En un solo comando: lee TASKS.md y mira `git status`, la rama actual y sus últimos commits.
2. Si hay una tarea sin cerrar, sitúate con el repo, no con la memoria: ¿hay spec en commit?
   ¿está aprobada en el tablero? ¿hay commits de tests o de implementación? ¿hay cambios sin
   commit? Lee .claude/kit/director.md y el SKILL.md del flujo (feature o fix) y localiza el
   paso que toca.
3. Si el tablero y el repo no coinciden, dilo y no sigas.
4. Resume el estado en pocas líneas y propón el siguiente paso. Si la tarea está aprobada o en
   curso y nada lo impide, continúa desde ese paso.
5. Si no hay ninguna tarea abierta, dilo en una línea y espera.
