---
name: adopt
description: Prepara el kit para un proyecto deduciendo componentes, comandos, documentos de referencia y convenciones, sin cambiar nada del proyecto. Se usa una vez, tras instalar el kit.
disable-model-invocation: true
---
El kit ya está instalado. No modifiques ningún fichero del proyecto: solo .claude/project.json,
CLAUDE.md y TASKS.md.

1. Inspecciona el repo actual y, si los hay, sus hermanos en el directorio superior con el mismo
   prefijo (por ejemplo, <proyecto>-backend y <proyecto>-frontend).
2. Deduce los componentes, su ruta y su stack. Marca como `readonly` los que no deban tocarse
   (por ejemplo, el repo de modelos del equipo de modelado) y confírmalo con el usuario.
3. Comandos de `build` y `test` de cada componente: mira Makefile, requirements, pytest.ini,
   .sln, README. Ejecuta los tests que haya para confirmar que el comando funciona y anota el
   resultado.
4. Entorno local: localiza los ficheros compose (docker-compose*.yml, compose*.yml) y los
   Dockerfile, sus servicios, puertos, redes externas y los .env que necesitan (.env.example).
   Anota en `run` de project.json los comandos que ya use el proyecto para levantar (`up`) y
   parar (`down`) y las comprobaciones de conectividad (`health`): la URL de salud de cada
   servicio web, `tcp://host:puerto` para la base de datos y, si existe, una llamada de
   extremo a extremo (ver el formato en .claude/scripts/smoke.py). No levantes ni pares nada
   sin permiso del usuario. Si el proyecto no tiene compose, deja `run` vacío, díselo al
   usuario y propón una tarea pendiente "Crear Dockerfile y compose de desarrollo";
   pregúntale si hay un proyecto de referencia del que copiar las convenciones. No lo crees
   tú en este comando.
5. Documentos de referencia: localiza specs, contratos, modelos de proceso, briefs, registros de
   progreso y ejemplos de respuesta. Propón al usuario la lista `references` en orden de
   autoridad.
6. Convenciones: nombres de rama (`git branch -a`), estilo de commits (`git log`), idioma de la
   interfaz y de los mensajes de error.
7. Remoto: mira `git remote -v` y si `gh` está instalado. Si no hay remoto, pregunta al usuario
   si lo habrá. Anota en "Propio de este proyecto" de CLAUDE.md cómo se cierran las tareas: con
   push y PR, o solo dejando el texto del PR en .claude/tmp/. Que falte el remoto no es una
   tarea pendiente si el usuario dice que no lo habrá.
8. Rellena project.json y la sección "Propio de este proyecto" de CLAUDE.md, incluidas las
   trampas que encuentres documentadas. No toques la línea que importa .claude/kit-rules.md.
   Pregunta al usuario si quiere cambiar alguna preferencia (`preferences` de project.json:
   tests, modo, smoke, navegador); si no, deja los valores por defecto.
9. Huecos (sin tests, contrato duplicado, secretos en ficheros versionados): propónlos como
   tareas pendientes en TASKS.md; no los resuelvas.
10. Enseña el resultado al usuario y ajusta lo que corrija.
