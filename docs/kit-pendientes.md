# idener-claude-kit: pendientes para la siguiente versión

Versión actual del kit: 0.5.1 (2026-10-06). Este fichero recoge lo que va saliendo al usar el kit en proyectos, para juntarlo en una nueva versión cuando haya material suficiente.

Regla para decidir: algo entra en el kit cuando se ha hecho a mano dos veces y ha costado; algo sale cuando no ha evitado ningún problema en cinco tareas.

## Apuntes del uso real

| Fecha | Proyecto | Qué pasó | Cambio propuesto |
|---|---|---|---|
| 2026-10-07 | REWET | El tablero ha vuelto a engordar: las filas de FB-42 y FB-43 son párrafos, y la regla era una línea por tarea. Se paga en cada sesión. | Tope concreto por fila (por ejemplo, 200 caracteres) en la guía del director y en la plantilla; que `/resume` avise cuando una fila se pase. La regla está hoy en `director.md`, que solo se lee al empezar un flujo. |
| 2026-10-07 | REWET | El agente paró la web para compilar sin preguntar, y luego hubo que relanzarla dentro de la sesión. Con una web .NET en marcha pasará en cada lote. | Regla: antes de compilar, mirar si hay algo levantado; si lo hay, avisar, pararlo y relanzarlo al terminar. Preferencia en `project.json` para indicar si se trabaja con la web siempre arriba. |

## Sin probar todavía (kit 0.5.1)

- «Sin flujo» con las reglas nuevas: crear la rama antes de tocar nada y pasar los tests al terminar. Falló en la 0.5.0 (T33 de RENEUMA) y se corrigió sin volver a medir.
- Modo sin tests y preferencias de `project.json`.
- Que el director proponga partir una tarea grande.
- `/fix` con un defecto real: test que falla primero.
- Bloqueo de escrituras fuera del proyecto en Windows.
- Proyecto con varios repos (`--role secondary`).

## Candidatos, a la espera de que el uso los pida

- Un comando para convertir una lista de mejoras en lotes (lo que en REWET se hizo a mano con un prompt: clasificar cada punto contra el código, unir repetidos, agrupar y registrar en el tablero).
- Repartir un Grant Agreement en tareas al arrancar un proyecto nuevo.
- Crear Dockerfile y compose a partir de un proyecto de referencia.
- Visor del tablero de solo lectura, tipo kanban.
- Agente para pruebas en el navegador, con su propia definición.
- `CLAUDE.md` de proyecto más corto: en RENEUMA ocupa más que las reglas del kit.

## Para retomar

- El código fuente está en el repo de GitHub `alegomgu/kit-develop-claude` (https://github.com/alegomgu/kit-develop-claude), rama `main`, desde la 0.5.1 (subida el 2026-10-07). Cualquier conversación puede clonarlo y devolver cambios; ya no hace falta subir el zip.
- La copia que se usa en los proyectos es la carpeta local de `IDENER_KIT`. Conviene que sea un clon de ese repo, para que haya una sola copia buena.
- El estado completo está en el `CHANGELOG.md` del kit, en `docs/guia-multiagente-idener.md` y en el documento «Kit multiagente para Claude Code en Idener: resumen y veredicto».
- Lo que salga en las conversaciones de cada proyecto (REWET y los siguientes) se trae aquí como una fila más de la primera tabla.
